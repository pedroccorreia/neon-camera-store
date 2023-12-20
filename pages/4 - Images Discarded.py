import streamlit as st
from constants import CATALOG_BUCKET, IMAGE_EXCLUSION_FILEPATH
from gcs_helper import delete_file_from_gcs, upload_dataframe_to_gcs
import ui_constants
import utils
import pandas as pd



removed_df = None
edited_removed_df = None

def remove_all():
    st.session_state['items_removed'] = []
    delete_file_from_gcs(CATALOG_BUCKET, IMAGE_EXCLUSION_FILEPATH)
    print("items removed")

def remove_selected():
    for index, row in edited_removed_df.iterrows():        
        if(row['select']==True):
            image_uri = row['image_uri']
            st.session_state[ui_constants.STATE_DISCARDED_IMAGES_KEY].remove(image_uri)
    save_all()
    st.empty()

def save_all():
    print("items saved")
    data = st.session_state[ui_constants.STATE_DISCARDED_IMAGES_KEY]
    # Create the DataFrame
    df = create_dataframe(data)
    upload_dataframe_to_gcs(df, CATALOG_BUCKET, IMAGE_EXCLUSION_FILEPATH  )

def create_dataframe(data):
    temp_data = []
    for entry in st.session_state[ui_constants.STATE_DISCARDED_IMAGES_KEY]:
        temp_data.append({'image_uri':entry, 'image': utils.transform_html_path(entry), 'select':False })
    # Create the DataFrame
    return pd.DataFrame(temp_data)


st.set_page_config(
    page_title="Images Discarded",
    page_icon="🗑️",
    layout="wide",    
)


if st.session_state[ui_constants.STATE_DISCARDED_IMAGES_KEY] == None or len(st.session_state[ui_constants.STATE_DISCARDED_IMAGES_KEY]) == 0:
    st.write("No items discarded")
else: 
    #prepare data
    data = st.session_state[ui_constants.STATE_DISCARDED_IMAGES_KEY]
    # Create the DataFrame
    removed_df = create_dataframe(data)
    st.write('# Images Discarded')
    
    
    cols = st.columns([1,10,1,1])
    cols[0].metric('Total items discarded' ,len(removed_df))
    cols[2].button('🗑️ All', on_click=remove_all)
    cols[3].button('🗑️ Selected', on_click=remove_selected)
    
    edited_removed_df = st.data_editor(removed_df,height=1500, hide_index=True, use_container_width=True,  column_config={
        "image": st.column_config.ImageColumn(
            "Preview Image", help="Preview your images", width="large"
        ),
        "select" :st.column_config.CheckboxColumn()
    },
    disabled=["image_uri", "Preview Image"]
    ,)

    # st.write()

