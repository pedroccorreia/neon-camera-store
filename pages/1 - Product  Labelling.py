
from services.data.firestore_service import FirestoreService
import utils
import vector_search as vs
import streamlit as st
import pandas as pd
import ui_constants
import re


from constants import INPUT_BUCKET, BUNDLE_FILENAME, CATALOG_FILEPATH
import gcs_helper as storage 


#init the data service
data_service = FirestoreService()


st.set_page_config(
    page_title="Product & Tag Recognizer",
    page_icon="🏷️",
    layout="wide",    
)


# Data handling
def get_bundles(filtered_images : None):
	bundles =  storage.load_jsonl_blob(INPUT_BUCKET, BUNDLE_FILENAME)
	
	#remove images that have been discarded if there are any
	if filtered_images != None:
		filtered_bundles =[]
		# go through all loaded bundles
		for bundle in bundles:
			# bundle only to be considered if the original not in the filtered images
			if bundle['original_image'] not in filtered_images: 
				# Bundle still being considered, but one of the similar images has been discarded
				filtered_similar_images = []
				for image in bundle['similar_images']:
					#remove the similar image if it's the same as the original
					if image['image_path'] not in filtered_images: 
						if image['image_path'] != bundle['original_image']:
							filtered_similar_images.append(image) #append the entire json object
							
				bundle['similar_images'] = filtered_similar_images
			
				# add the newly entry
				filtered_bundles.append(bundle)
			
	#update image urls
	for bundle in filtered_bundles:
		utils.transform_bundle_html_path(bundle)
	
	print(f'''Returning {len(filtered_bundles)} bundles | {len(filtered_images)} filtered images''')
	return filtered_bundles

@st.cache_data
def load_article_data():
	# Read the CSV file into a Pandas DataFrame
	data = pd.read_csv(CATALOG_FILEPATH)
	data['URL']  = "https://www.woolworths.com.au/shop/productdetails/" + data['Article ID'].astype(str)
	# add column for editing
	data['choose'] = False
	return data

# returns an array of bundles removing all images that have been discared
def get_filtered_bundles(category_filter=None):
	discarded_images = data_service.get_discarded_uris()
	catalog_images = data_service.get_catalog_uris()
	print(f'discared Images {len(discarded_images)} | catalog_images {len(catalog_images)}')
	filtered_images = discarded_images + catalog_images
	
	bundles = get_bundles(filtered_images)

	#Category filtering
	res = []
	for bundle in bundles:
		if category_filter is None or category_filter in bundle['original_image']:
			res.append(bundle)
	return res

def navigate_to_detail(id):
	st.session_state.image_comparison = id
	# move to detail
	st.session_state[ui_constants.PRODUCT_LABELLING_PAGE_TYPE_KEY] = ui_constants.PRODUCT_LABELLING_PAGE_TYPE_DETAIL

def navigate_to_list():
	st.session_state.image_comparison = None
	# move to list
	st.session_state[ui_constants.PRODUCT_LABELLING_PAGE_TYPE_KEY] = ui_constants.PRODUCT_LABELLING_PAGE_TYPE_LIST


def navigate_to_article():
	# move to list
	st.session_state[ui_constants.PRODUCT_LABELLING_PAGE_TYPE_KEY] = ui_constants.PRODUCT_LABELLING_PAGE_TYPE_ARTICLE


def update_product_catalog(bundle):
	article_id = st.session_state[ui_constants.STATE_ARTICLE_CHOSEN_KEY]
	print(f'''Updating catalog for article: {article_id}''')

	if article_id != None:	
		# convert the bundle into an array of json objects that have: 
		# +article id, +image url (to be imported to the model), original image url (current location), +image id (unique auto generated)
		new_entries = utils.transform_bundle_to_catalog(  bundle, article_id)
		#add it to the added bundles
		data_service.add_catalog_entries(new_entries)
		
		# move to list
		st.session_state[ui_constants.PRODUCT_LABELLING_PAGE_TYPE_KEY] = ui_constants.PRODUCT_LABELLING_PAGE_TYPE_LIST

def handle_discard_bundle(bundle):
	bundle = utils.transform_bundle_gcs_uri(bundle)
	
	#adding initial image
	data_service.add_discarded(image_uri=bundle['filename'])
	for similar_image in bundle['similar_images']:
		data_service.add_discarded(image_uri=similar_image['image_path'])
	
	# move to list
	st.session_state[ui_constants.PRODUCT_LABELLING_PAGE_TYPE_KEY] = ui_constants.PRODUCT_LABELLING_PAGE_TYPE_LIST

def handle_discard_image(uri):
	remove_path = uri
	bundle = st.session_state['image_comparison']
	new_images=[]
	for similar_image in bundle['similar_images']:
		if similar_image['image_path'] != remove_path:
			print(f'''{remove_path} {similar_image['image_path']}''')
			new_images.append(similar_image)
		else:
			#item is on the remove path
			new_uri = utils.transform_gcs_uri(similar_image['image_path'])
			#update the data service with the new entry
			data_service.add_discarded(image_uri=new_uri)

	
	bundle['similar_images'] = new_images
	st.session_state['image_comparison'] = bundle

# Start up navigation and state info
if  ui_constants.PRODUCT_LABELLING_PAGE_TYPE_KEY not in st.session_state:
    st.session_state[ui_constants.PRODUCT_LABELLING_PAGE_TYPE_KEY] = ui_constants.PRODUCT_LABELLING_PAGE_TYPE_LIST

if 'items_removed' not in st.session_state:
    st.session_state.items_removed = []


# Build different Pages

def build_list_page():
	st.write("# Product Labelling")
	with st.form("my_form"):
		st.write("Pick a Category")
		selected_index = 0
		if ui_constants.PRODUCT_LABELLING_PAGE_CATEGORY_FILTER in st.session_state:
			selected_index = utils.category_filter_selected_index(st.session_state[ui_constants.PRODUCT_LABELLING_PAGE_CATEGORY_FILTER])
			
		category_filter = st.selectbox( 'What categories would you like to map', ('None', 'Bread', 'Cofee', 'Meat', 'Soft Drinks', 'Tea' ), index=selected_index)
		st.session_state[ui_constants.PRODUCT_LABELLING_PAGE_CATEGORY_FILTER] = category_filter
		
		working_set = st.slider('Choose a set of images', 5, 50, value=15, step=5)
		form_submitted = st.form_submit_button('Get Bundles')
		#get all the files in a the input bucket
		filter_expression = None
		if category_filter != 'None':
			filter_expression = category_filter.lower()
			filter_expression = filter_expression.replace(' ', "_")

		bundles = get_filtered_bundles(filter_expression)
		
	with st.container():
		filtered_image_paths =[]
		for bundle in bundles:
			image_path = bundle['original_image']
			# Extract the category using regular expressions
			category = re.findall( "bread|cofee|meat|soft.drink|tea", image_path, re.IGNORECASE)[0]
			
			filtered_image_paths.append( {  'path': image_path, 'filename' : image_path, 'category' : category, 'similar_images' : bundle['similar_images'] })
			if len(filtered_image_paths) == working_set:
				break


		
		
		st.write('## Bundles')
		st.divider()
		for bundle in filtered_image_paths:
			cols = st.columns([8,1,1]) # number of columns in each row! = 2
			# first column of the ith row
			cols[0].image( bundle['path'], width=400)
			# cols[1].text(bundle['filename']) 
			# cols[2].text(bundle['category'])
			cols[1].button('Discard', type="primary",key='discard_'+bundle['path'], on_click=handle_discard_bundle, args=[bundle])
			cols[2].button('View Bundle', key='similar_'+bundle['path'], on_click=navigate_to_detail, args=[bundle] )
	
def build_detail_page():
	st.write("# Product Labelling > Detail")
	st.button('← Go Back', on_click=navigate_to_list)
    
	bundle = st.session_state['image_comparison']
	
	 
	with st.container():
		cols = st.columns([6,1,1])
		
		cols[1].button('🛑 Discard Bundle', on_click=handle_discard_bundle, args=[bundle])
		cols[2].button('📋 Choose Article', on_click=navigate_to_article)
	
	st.divider()
	st.write("### Starting image")
	with st.container():
		cols = st.columns([1,1,1])
		cols[0].image( bundle['path'], width=500)
		cols[1].metric(label='Category', value=bundle["category"])
		cols[2].metric(label='Similar Images', value=len(bundle['similar_images']))
    

	st.divider()
	st.write("#### Similar Images")    
	for index, similar_image in enumerate(bundle['similar_images']):
		cols = st.columns(3)    
		cols[0].image ( similar_image['image_path'], width=300 )
		cols[1].text ( similar_image['similarity_score'])
		cols[2].button( 'remove', on_click=handle_discard_image, key=index, args=[similar_image['image_path']])

def build_article_page():
	st.write("# Product Labelling > Article")
	#init article chose
	if ui_constants.STATE_ARTICLE_CHOSEN_KEY not in st.session_state:
		print('setting chosen article to none')
		st.session_state[ui_constants.STATE_ARTICLE_CHOSEN_KEY] = None

	bundle = st.session_state['image_comparison']
	st.write("Images chosen:")
	cols = st.columns(len(bundle['similar_images'])+1)
	cols[0].image(bundle['filename'], width=500, caption='Seed')
	for index, similar_image  in enumerate(bundle['similar_images']):
		cols[index+1].image(similar_image['image_path'], width=300, caption='Similar')
	
	st.write("## Choose the article for this bundle")
	with st.container():
		cols = st.columns([1,6,1,1])
		cols[0].button('← Go Back', on_click=navigate_to_detail, args=[st.session_state.image_comparison])
		cols[1].text('Options for Bundle')
		cols[2].button('🛑 Discard Bundle', on_click=handle_discard_bundle, args=[bundle])
		cols[3].button('✅ Add Bundle', on_click=update_product_catalog, args=[bundle])
		
	df = load_article_data()
	
	edited_df = st.data_editor(df, column_config={
        "choose": st.column_config.CheckboxColumn(
            "Choose article",
            help="Select the **correct** article for this bundle",
            default=False,
        ), 
		"Article ID" :st.column_config.TextColumn(),
		"URL":st.column_config.LinkColumn()
    },
	disabled=["Article ID", "Name","Category", "Sub-Category"],
    hide_index=True,
	use_container_width=True) # 👈 An editable dataframe
	
	chosen_article = edited_df.loc[edited_df["choose"].isin([True])]
	
	if chosen_article.shape[0] > 0: #picks the first choice
		article = chosen_article.head(1)["Article ID"].values[0]
		st.session_state[ui_constants.STATE_ARTICLE_CHOSEN_KEY] = article
		print(f'setting chosen article {article}')
	

#Overall Page Creation
if st.session_state[ui_constants.PRODUCT_LABELLING_PAGE_TYPE_KEY] == ui_constants.PRODUCT_LABELLING_PAGE_TYPE_LIST:
    st.empty()
    build_list_page()
elif st.session_state[ui_constants.PRODUCT_LABELLING_PAGE_TYPE_KEY] == ui_constants.PRODUCT_LABELLING_PAGE_TYPE_DETAIL:
	st.empty()
	build_detail_page()
elif st.session_state[ui_constants.PRODUCT_LABELLING_PAGE_TYPE_KEY] == ui_constants.PRODUCT_LABELLING_PAGE_TYPE_ARTICLE:
	st.empty()
	build_article_page()

	
