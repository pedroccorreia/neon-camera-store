import streamlit as st
from gcs_helper import load_json_blob 
from constants import RUNS_BUCKET, CONSOLIDATED_FOLDER, IMAGE_EXTENSION
from utils import run_recognition_metrics, transform_html_path, get_image_id
import ui_constants
import pandas as pd


st.set_page_config(
    page_title="Results",
    page_icon="📸",
    layout="wide",    
)

@st.cache_data
def get_run_results(run_id):
    file_path = run_id + '/'+ CONSOLIDATED_FOLDER + '/final.jsonl'
    result = load_json_blob(RUNS_BUCKET, file_path)
    return result

def get_run_results_per_image(run_id, filtering_image_id):
    run_results = get_run_results(run_id=run_id)
    results = []
    for entry in run_results:
        filename = get_image_id(entry['original_image_uri'])
        if filtering_image_id == filename:
            results.append(entry)
    return results

# Given a  result run will create a list of images
def image_list(run_info):
    image_keys = []
    image_uri = []
    for entry in run_info:
        image_id = entry['imageUri'].split("/")[-2]
        if image_id not in image_keys:
            image_keys.append(image_id)
            image_uri.append(entry['original_image_uri'])
    return list(zip(image_keys,image_uri))


def get_header_images(run_id, image_uri):
    image_uri = image_uri + IMAGE_EXTENSION
    return {
        'original_image_uri' : transform_html_path(RUNS_BUCKET+'/'+run_id+'/original/'+ image_uri),
        'detection_image_uri' : transform_html_path(RUNS_BUCKET+'/'+run_id+'/detection/'+image_uri),
        'recognition_image_uri' : transform_html_path(RUNS_BUCKET+'/'+run_id+'/consolidated/images/'+image_uri)
    }

@st.cache_data
def get_run_list():
    # Create a Pandas DataFrame with static data
    data = [
        {"run_id": 'bread_20231128-051003', "catalog_info": "", "observation": "none"},
        {"run_id": 'bread__20231129-000523', "catalog_info": "", "observation": "18 products added"},
    ]
    return data


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

#Build different pages
def build_detail_page():
    run_id = st.session_state['run_id']
    image_uri = st.session_state['image_uri']
    image_id = get_image_id(image_uri)
    st.write(f'## Run ID: {run_id}')
    st.write(f'### Image: {get_image_id(image_uri)}')
    #TODO: Run Result table
    # Builds Image Row
    image_uri_info = get_header_images(run_id, image_id)
    st.button('← Go back',on_click=navigate_to_run, args=[run_id])

    cols = st.columns(3)
    cols[0].header('Original Image')
    cols[0].image(image_uri_info['original_image_uri'])
    cols[1].header('Products Detected')
    cols[1].image(image_uri_info['detection_image_uri'])
    cols[2].header('Products Recognized')
    cols[2].image(image_uri_info['recognition_image_uri'])

    run_results = get_run_results_per_image(run_id, image_id)
    
    st.write('## Run Details')
    st.write(f''' Number of Results {len(run_results)} ''')

    with st.expander("Product Details"):
        st.write("This shows the unique product detected in the image")
        metrics = run_recognition_metrics(run_results)
        st.dataframe(data=metrics, use_container_width=True, hide_index=True)
        

    with st.expander("Image Details"):
        col1,col2, col3, col4, col5 = st.columns([4,1,2,2,1])
        col1.subheader('Image')
        col2.subheader('Result')
        col3.subheader('Product')
        col4.subheader('Confidence')
        col5.subheader('    ')
        for entry in run_results:
            col1,col2, col3, col4, col5 = st.columns([4,1,2,2,1])
            
            col1.image(transform_html_path(entry['imageUri'])) # Consolidated view
            if(len(entry['productRecognitionAnnotations'][0]['recognitionResults']) == 0):
                col2.text('🔴')
            else:
                rec_result = entry['productRecognitionAnnotations'][0]['recognitionResults'][0]
                prod_data = entry['productRecognitionAnnotations'][0]['recognitionResults'][0]['productMetadata']
                col2.text(f'''🟢''')
                col3.text(prod_data['title'])
                col4.text(round(rec_result['confidence'],ndigits=2))
                col5.button('Detail', key=entry['imageUri'], on_click=navigate_to_rec_detail, args=[entry])
    

def build_list_page():
    st.write("# All runs performed")
    runs = get_run_list()
    # Create columns for table and buttons
    col1, col2, col3, col4 = st.columns(4)
    for run in runs:
        with col1:
            st.text(run['run_id'])
        with col2:
            st.text(run['catalog_info'])
        with col3:
            st.text(run['observation'])
        with col4:
            st.button('Detail', key=run['run_id'], on_click=navigate_to_run,args=[run['run_id']])

    
def build_run_page():
    run_id = st.session_state['run_id']
    st.write("# Run Page")
    st.write(f'''Run: {run_id}''')
    st.button('← Go back',on_click=navigate_to_list)

    results = image_list(get_run_results(run_id=run_id))
    with st.container(border=True):
        for result in results:
            cols = st.columns([4,1,1])
            image_uri = result[1]
            cols[0].image(transform_html_path(image_uri), width=600)
            cols[1].text(result[0])
            cols[2].button('Detail', key=result[0], on_click=navigate_to_run_detail, args=[run_id, image_uri])
            
        
    # st.button('Detail', on_click=navigate_to_run_detail, args=[run_id, image_uri] )

def build_rec_results_page():
    run_id = st.session_state['run_id']
    image_id = st.session_state['image_uri']
    #json object with all the info on the recognition result for this image
    recognition_entry = st.session_state[ui_constants.STATE_RECOGNITION_RESULTS_KEY]
    
    st.button('← Go back',on_click=navigate_to_run_detail, args=[run_id, image_id])
    st.write("# Recognition Results")
    #show json content
    st.json(recognition_entry)




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