import streamlit as st
from constants import CATALOG_BUCKET, CATALOG_UPDATES_FILEPATH
from gcs_helper import delete_file_from_gcs, upload_dataframe_to_gcs
from state_management import save_catalog
import ui_constants
import pandas as pd
import utils



#init

catalog_df = None
edited_df = None


st.set_page_config(
    page_title="Product Catalog",
    page_icon="📋",
    layout="wide",    
)


def discard_all():
    del st.session_state[ui_constants.STATE_ADDED_BUNDLES_KEY]
    delete_file_from_gcs(CATALOG_BUCKET, CATALOG_UPDATES_FILEPATH)

def discard_selected():
    selected_uri = []
    for index, row in edited_df.iterrows():        
        
        if(row['select']==True):
            print(f'Current items {len(st.session_state[ui_constants.STATE_ADDED_BUNDLES_KEY])}')
            # print(st.session_state[ui_constants.STATE_ADDED_BUNDLES_KEY])
            gcs_uri = utils.transform_gcs_uri(row['image'])
            filtered_array = [item for item in st.session_state[ui_constants.STATE_ADDED_BUNDLES_KEY] if item['original_image_uri'] != gcs_uri]

            st.session_state[ui_constants.STATE_ADDED_BUNDLES_KEY] = filtered_array
            print(f'Removed items now catalog has: {len(st.session_state[ui_constants.STATE_ADDED_BUNDLES_KEY])}')
            
            
            
    save_catalog(st.session_state[ui_constants.STATE_ADDED_BUNDLES_KEY])
            

    

def create_dataframe(data):
    temp_data = []
    for entry in data:
        temp_data.append({'Article': entry['article_id'], 'URL' : 'http://woolworths.com.au/shop/productdetails/'+str(entry['article_id']), 'image': utils.transform_html_path(entry['original_image_uri']), 'select':False})
    # Create the DataFrame
    return pd.DataFrame(temp_data)

if ui_constants.STATE_ADDED_BUNDLES_KEY not in st.session_state or len(st.session_state[ui_constants.STATE_ADDED_BUNDLES_KEY]) == 0:
    st.write("No items chosen to update catalog")
else: 

    #data
    data = st.session_state[ui_constants.STATE_ADDED_BUNDLES_KEY]
    
    # Create the DataFrame
    catalog_df = create_dataframe(data)

    # Copy the catalog_df into a metrics_df that will add row
    metrics_df = catalog_df.copy()
    # Calculate number items in the dataframe
    totalRows = len(catalog_df.index)
    # Calculate unique values in the Article column
    uniqueRows = len(catalog_df['Article'].unique())
    # Calculate overall average of the number of rows per Article
    averageRows = totalRows / uniqueRows

    # Display the metrics in table
    st.write('# Catalog')
    cols = st.columns(3)
    cols[0].metric("Total Entries", totalRows)
    cols[1].metric("Unique Articles", uniqueRows)
    cols[2].metric("Average images per article", averageRows)

    cols = st.columns([10,1,2])
    cols[1].button('🗑️ All', on_click=discard_all)
    cols[2].button('🗑️ Selected', on_click=discard_selected)

    edited_df = st.data_editor(catalog_df, height=1500, hide_index=True, use_container_width=True,  column_config={
        "Article" : st.column_config.TextColumn(),
        "image": st.column_config.ImageColumn(
            "Preview Image", help="Preview your images", width="large"
        ),
        "URL" : st.column_config.LinkColumn(),
        "select" :st.column_config.CheckboxColumn()
    },
    disabled=["Article", "Preview Image"]
    ,)

