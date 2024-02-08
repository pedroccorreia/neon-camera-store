import math
import constants
from services.runs.run_service import RunService
import utils
import streamlit as st
from services.data.firestore_service import FirestoreService
from constants import RUNS_BUCKET,IMAGE_EXTENSION
from services.match.matching_service import MatchingService
from utils import run_recognition_metrics, transform_html_path, get_image_id
import ui_constants
import pandas as pd


st.set_page_config(
    page_title="Results",
    page_icon="📸",
    layout="wide",    
)

#init the services
data_service = FirestoreService()
run_service = RunService()


def get_header_images(run_id, image_uri):
    image_uri = image_uri + IMAGE_EXTENSION
    return {
        'original_image_uri' : transform_html_path(RUNS_BUCKET+'/'+run_id+'/original/'+ image_uri),
        'detection_image_uri' : transform_html_path(RUNS_BUCKET+'/'+run_id+'/detection/'+image_uri),
        'recognition_image_uri' : transform_html_path(RUNS_BUCKET+'/'+run_id+'/consolidated/images/'+image_uri)
    }


def get_run_list():
    # Create a Pandas DataFrame with firestore data
    columns = ['id', 'catalog', 'category', 'observations', 'run_date', 'visible']

    data = data_service.get_recognition_runs(filter_visible=True)
    
    return pd.DataFrame(data,columns=columns)


def navigate_to_list():
    st.session_state['run_id'] = None
    st.session_state[ui_constants.PRODUCT_RECOGNITION_PAGE_TYPE_KEY] = ui_constants.PRODUCT_RECOGNITION_PAGE_TYPE_LIST

# Navigation Handlers
def navigate_to_run(run_id):
    st.session_state['run_id'] = run_id
    st.session_state['image_uri'] = None
    st.session_state[ui_constants.PRODUCT_RECOGNITION_PAGE_TYPE_KEY] = ui_constants.PRODUCT_RECOGNITION_PAGE_TYPE_RUN

def navigate_to_run_detail(run_id, image_uri):
    st.session_state['run_id'] = run_id
    st.session_state['image_uri'] = image_uri
    st.session_state[ui_constants.PRODUCT_RECOGNITION_PAGE_TYPE_KEY] = ui_constants.PRODUCT_RECOGNITION_PAGE_TYPE_DETAIL

def navigate_to_rec_detail(rec_result):
    st.session_state[ui_constants.STATE_RECOGNITION_RESULTS_KEY] = rec_result
    st.session_state[ui_constants.PRODUCT_RECOGNITION_PAGE_TYPE_KEY] = ui_constants.PRODUCT_LABELLING_PAGE_TYPE_REC_RESULTS


def navigate_to_product_labelling( image_uri):
    st.session_state[ui_constants.STATE_CHOSEN_IMAGE_TO_LABEL] = image_uri
    st.session_state[ui_constants.PRODUCT_RECOGNITION_PAGE_TYPE_KEY] = ui_constants.PRODUCT_RECOGNITION_LABEL_SEARCH

def navigate_exit_labelling():
	# remove previously existing image chosen
	if ui_constants.STATE_CHOSEN_IMAGE_TO_LABEL in st.session_state:
		del st.session_state[ui_constants.STATE_CHOSEN_IMAGE_TO_LABEL]
	if ui_constants.STATE_CHOSEN_SIMILAR_IMAGES in st.session_state:
		del st.session_state[ui_constants.STATE_CHOSEN_SIMILAR_IMAGES]
          
	navigate_to_run_detail(st.session_state['run_id'], st.session_state['image_uri'])

def navigate_to_article():
    st.session_state[ui_constants.PRODUCT_RECOGNITION_PAGE_TYPE_KEY] = ui_constants.PRODUCT_RECOGNITION_LABEL_ARTICLE

#Event handlers
def handle_toggle_image(image_uri):
    chosen_images=[]
    if ui_constants.STATE_CHOSEN_SIMILAR_IMAGES in st.session_state:
        chosen_images = st.session_state[ui_constants.STATE_CHOSEN_SIMILAR_IMAGES]
    
    if image_uri in chosen_images:
        chosen_images.remove(image_uri)
    else:   
        chosen_images.append(image_uri)

    st.session_state[ui_constants.STATE_CHOSEN_SIMILAR_IMAGES] = chosen_images
    
def handle_add_product_catalog(): 
    article_id = st.session_state[ui_constants.STATE_ARTICLE_CHOSEN_KEY]
    print(f'''Updating catalog for article: {article_id}''')

    if article_id != None:	
        chosen_images = st.session_state[ui_constants.STATE_CHOSEN_SIMILAR_IMAGES]
        new_entries = []
        for image in chosen_images:
            gcs_uri = utils.transform_gcs_uri(image)
            print(f'adding {image} to article {article_id}')
            new_entries.append({'article_id': article_id, 'image_uri' : gcs_uri, 'original_image_uri' : gcs_uri})
        #add it to the catalog
        data_service.add_catalog_entries(new_entries, source=constants.LABELLING_SOURCE_RUNS)
        navigate_exit_labelling()
    

#Build different pages
def build_detail_page():
    run_id = st.session_state['run_id']
    image_uri = st.session_state['image_uri']
    image_id = get_image_id(image_uri)
    st.write(f'## Run ID: {run_id} | Image: {image_id}')
    
    # Builds Image Row
    image_uri_info = get_header_images(run_id, image_id)
    st.button('← Go back',on_click=navigate_to_run, args=[run_id])
    run_results = run_service.get_run_results_per_image(run_id, image_id)
    metrics = run_recognition_metrics(run_results)

    #Calculate Metrics
    filtered_df = metrics[metrics['Products'] == 'No Product Matched']
    num_no_products_found = (100-filtered_df.sum()['Percentage of total'])
    unique_products = metrics['Products'].nunique()
    
    # Image Headers
    st.write('Images')
    cols = st.columns(3)
    cols[0].image(image_uri_info['original_image_uri'], caption='Original Image')
    cols[1].image(image_uri_info['detection_image_uri'], caption='Products Detected')
    cols[2].image(image_uri_info['recognition_image_uri'], caption='Products Recognized')

    st.divider()
    st.write('Metrics')
    cols = st.columns(3)
    cols[0].metric('Product Facings', len(run_results))
    cols[1].metric('Products Found %', num_no_products_found)
    cols[2].metric('Unique Products', unique_products if num_no_products_found == 0 else unique_products - 1)
    
    with st.expander("Product Details", expanded=False):
        st.write("This shows the unique product detected in the image")
        st.dataframe(data=metrics, use_container_width=True, hide_index=True)

    with st.expander("Products Detected", expanded=True):
        grid_columns = 3
        total_rows = math.ceil(len(run_results)/grid_columns)
        cols = st.columns(3)
        current_index = 0
        for i in range(total_rows):
            row_container  = st.container()
            cols = row_container.columns(grid_columns)
            for col_index in range(grid_columns):
                if current_index < len(run_results):
                    with cols[col_index]:
                        with st.container(border=True):
                            entry = run_results[current_index]
                            product_found_flag = len(entry['productRecognitionAnnotations'][0]['recognitionResults']) != 0
                            if(not(product_found_flag)):
                                image_col, spacer, detail_col = st.columns([2,1,4])
                                detail_col.text('No product Found')
                                image_col.image(transform_html_path(entry['imageUri'])) # Consolidated view
                                detail_col.text('🔴')
                                detail_col.button('Detail', key=entry['imageUri'] + '-detail', on_click=navigate_to_rec_detail, args=[entry])
                                detail_col.button('Label', key= entry['imageUri'] + '-label', type='primary', on_click=navigate_to_product_labelling, args=[entry['imageUri']])
                
                            else:
                                rec_result = entry['productRecognitionAnnotations'][0]['recognitionResults'][0]
                                prod_data = entry['productRecognitionAnnotations'][0]['recognitionResults'][0]['productMetadata']
                    
                                image_col, spacer, detail_col = st.columns([2,1,4])
                                detail_col.text(prod_data['title'])
                                image_col.image(transform_html_path(entry['imageUri'])) # Consolidated view
                                # r
                                # detail_col.text(round(rec_result['confidence'],ndigits=2))
                                detail_col.progress(round(rec_result['confidence'],ndigits=2), text='Confidence')
                                detail_col.text(round(rec_result['confidence'],ndigits=2))
                                detail_col.button('Detail', key=entry['imageUri'] + '-detail', on_click=navigate_to_rec_detail, args=[entry])
                                detail_col.button('Label', key= entry['imageUri'] + '-label', type='primary', on_click=navigate_to_product_labelling, args=[entry['imageUri']])
                        current_index = current_index + 1
                                    

def build_list_page():
    st.write("# All runs performed")
    run_df = get_run_list()

    #order the dataframe for descending date
    run_df = run_df.sort_values(by=['run_date'], ascending=False)
    
    
    # Create columns for table and buttons
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.subheader('Run ID')
    col2.subheader('Catalog Info')
    col3.subheader('Observation')
    col4.subheader('Date')
    col5.subheader('Category')
    
    for index, row in run_df.iterrows():
        with st.container():
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            col1.text(row['id'])
            col2.text(row['catalog'])
            col3.text(row['observations'])
            col4.text(row['run_date'].date())
            col5.text(row['category'])
            col6.button('Detail', key=row['id'], on_click=navigate_to_run,args=[row['id']], use_container_width=False)
        # st.divider()r
           
    
def build_run_page():
    run_id = st.session_state['run_id']
    st.write("# Run Page")
    st.write(f'''Run: {run_id}''')
    st.button('← Go back',on_click=navigate_to_list)

    results = run_service.image_list(run_service.get_run_results(run_id=run_id))


    image_set = [row[1] for row in results]
    run_results = run_service.get_run_results_per_image_set(run_id, image_set)
    metrics = run_recognition_metrics(run_results)

    #Calculate Metrics
    filtered_df = metrics[metrics['Products'] == 'No Product Matched']
    num_no_products_found = (100-filtered_df.sum()['Percentage of total'])
    unique_products = metrics['Products'].nunique()

    st.write('## Metrics')
    cols = st.columns(4)
    cols[0].metric('Images', len(image_set))
    cols[1].metric('Product Facings', len(run_results))
    cols[2].metric('Products Found %', num_no_products_found)
    cols[3].metric('Unique Products', unique_products if num_no_products_found == 0 else unique_products - 1)
    
    
    with st.expander("Product Details", expanded=False):
        st.dataframe(data=metrics, use_container_width=True, hide_index=True)
    
    with st.expander("Details", expanded=True):
        cols = st.columns([2,1,1])
        cols[0].subheader('Image')
        cols[1].subheader('ID')
        cols[2].subheader('Actions')
            
        for result in results:
            
            image_uri = result[1]

            with st.container():
                cols = st.columns([2,1,1])
                cols[0].image(transform_html_path(image_uri), width=600)
                cols[1].text(result[0])
                cols[2].button('Detail', key=result[0], on_click=navigate_to_run_detail, args=[run_id, image_uri])
                
        
    

def build_rec_results_page():
    run_id = st.session_state['run_id']
    image_id = st.session_state['image_uri']
    #json object with all the info on the recognition result for this image
    recognition_entry = st.session_state[ui_constants.STATE_RECOGNITION_RESULTS_KEY]
    
    st.button('← Go back',on_click=navigate_to_run_detail, args=[run_id, image_id])
    st.write("# Recognition Results")
    #show json content
    st.json(recognition_entry)
    
def get_number_similar_images():
    return 0 if ui_constants.STATE_CHOSEN_SIMILAR_IMAGES not in st.session_state else len(st.session_state[ ui_constants.STATE_CHOSEN_SIMILAR_IMAGES])

#TODO: make this reusable
@st.cache_data
def load_article_data():
	# Read the CSV file into a Pandas DataFrame
	data = pd.read_csv(constants.CATALOG_FILEPATH)
	data['URL']  = "https://www.woolworths.com.au/shop/productdetails/" + data['Article ID'].astype(str)
	# add column for editing
	data['choose'] = False
	return data
     
#page that will enable the user to search similar images for a chosen image
def build_label_search_page():
    st.write("## Choose Images")
    image_id = st.session_state[ui_constants.STATE_CHOSEN_IMAGE_TO_LABEL]

    contains_image = data_service.contains_catalog(data_service.get_image_id_from_run(image_id))

    with st.container():
       cols = st.columns([1,2,2,4,6])
       cols[0].button('← Go Back', on_click=navigate_exit_labelling)
       cols[1].button('📋 Choose Article', on_click=navigate_to_article)
       
       cols[4].metric(label='Similar Images', value=get_number_similar_images())
       
       if contains_image:
        cols[3].metric(label='Used before', value='⛔️')
       else:
           cols[3].metric(label='Not used before', value='✅')
       
    
    st.divider()
    st.write("#### Images")    
    #create Matching Service
    matching_service = MatchingService()
    similarity_results = matching_service.get_matches(image_id)
    # st.table(similarity_results)

    with st.container():
        total_rows = math.ceil(len(similarity_results)/4)
        current_index = 0
        for row_index in range(total_rows):
            row_container = st.container()
            # Create 4 columns in this row
            cols = row_container.columns(4)
            for col_index in range(4):
                if current_index < len(similarity_results):
                    similar_image = similarity_results[current_index]
                    with cols[col_index]:
                        caption = f'Similarity: { round(1-similar_image[1],3)}' if current_index != 0 else '⭐️ Original'
                            
                        st.image(similar_image[0], width=250, caption=caption)
                        st.toggle(label="Include", 
                            key=similar_image[0], 
                            value = False,
                            on_change= handle_toggle_image, args=[similar_image[0]]
                        )
                    current_index = current_index + 1
            
            
def build_label_article_page():
	st.write("## Choose Article")
    
	#init article chose
	if ui_constants.STATE_ARTICLE_CHOSEN_KEY not in st.session_state:
		print('setting chosen article to none')
		st.session_state[ui_constants.STATE_ARTICLE_CHOSEN_KEY] = None


	# bundle = st.session_state['image_comparison']
	st.write("Images chosen:")
	similar_images = st.session_state[ui_constants.STATE_CHOSEN_SIMILAR_IMAGES]
	cols = st.columns(len(similar_images))
	
	for index, similar_image  in enumerate(similar_images):
		cols[index].image(similar_image, width=100)

	st.write("## Choose the article for this bundle")
	with st.container():
		cols = st.columns([1,6,1,1])
		cols[0].button('← Go Back', on_click=navigate_exit_labelling)
		cols[1].text('Options')
		cols[3].button('✅ Add Article', on_click=handle_add_product_catalog)
		
	df = load_article_data()
	df = df.sort_values("Name")
	
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
        
        
# Overall page creation
if  ui_constants.PRODUCT_RECOGNITION_PAGE_TYPE_KEY not in st.session_state:
    st.session_state[ui_constants.PRODUCT_RECOGNITION_PAGE_TYPE_KEY] = ui_constants.PRODUCT_RECOGNITION_PAGE_TYPE_LIST

if st.session_state[ui_constants.PRODUCT_RECOGNITION_PAGE_TYPE_KEY] == ui_constants.PRODUCT_RECOGNITION_PAGE_TYPE_LIST:
    st.empty()
    build_list_page()
elif st.session_state[ui_constants.PRODUCT_RECOGNITION_PAGE_TYPE_KEY] == ui_constants.PRODUCT_RECOGNITION_PAGE_TYPE_RUN:
    st.empty()
    build_run_page()
elif st.session_state[ui_constants.PRODUCT_RECOGNITION_PAGE_TYPE_KEY] == ui_constants.PRODUCT_RECOGNITION_PAGE_TYPE_DETAIL:
    st.empty()
    build_detail_page()
elif st.session_state[ui_constants.PRODUCT_RECOGNITION_PAGE_TYPE_KEY] == ui_constants.PRODUCT_LABELLING_PAGE_TYPE_REC_RESULTS:
    st.empty()
    build_rec_results_page()
elif st.session_state[ui_constants.PRODUCT_RECOGNITION_PAGE_TYPE_KEY] == ui_constants.PRODUCT_RECOGNITION_LABEL_SEARCH:
    st.empty()
    build_label_search_page()
elif st.session_state[ui_constants.PRODUCT_RECOGNITION_PAGE_TYPE_KEY] == ui_constants.PRODUCT_RECOGNITION_LABEL_ARTICLE:
    st.empty()
    build_label_article_page()