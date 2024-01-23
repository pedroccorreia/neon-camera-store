import streamlit as st
from constants import CATALOG_BUCKET, IMAGE_EXCLUSION_FILEPATH
from services.gcs_service import delete_file_from_gcs, upload_dataframe_to_gcs
from services.data.firestore_service import FirestoreService
import ui_constants
import utils
import pandas as pd



removed_df = None
edited_removed_df = None

#init the data service
data_service = FirestoreService()

def remove_selected():
    for index, row in edited_removed_df.iterrows():        
        if(row['select']==True):
            image_uri = row['image_uri']
            data_service.remove_discarded(image_uri)
    st.empty()


def create_dataframe(data):
    temp_data = []
    for entry in data:
        # set visible and editable parts of the table
        entry['image'] = utils.transform_html_path(entry.get('image_uri'))
        entry['select'] = False
        temp_data.append(entry)
    
    # Create the DataFrame
    return pd.DataFrame(temp_data)


st.set_page_config(
    page_title="Images Discarded",
    page_icon="🗑️",
    layout="wide",    
)


if not data_service.has_discarded():
    st.write("No items discarded")
else: 
    #prepare data
    data = data_service.get_discarded()
    # Create the DataFrame
    removed_df = create_dataframe(data)
    st.write('# Images Discarded')
    
    
    cols = st.columns([1,10,1])
    cols[0].metric('Total items discarded' ,len(removed_df))
    cols[2].button('🗑️ Selected', on_click=remove_selected)
    
    edited_removed_df = st.data_editor(removed_df,height=1500, hide_index=True, use_container_width=True,  column_config={
        "image": st.column_config.ImageColumn(
            "Preview Image", help="Preview your images", width="large"
        ),
        "select" :st.column_config.CheckboxColumn()
    },
    disabled=["image_uri", "Preview Image"]
    ,)



