import streamlit as st
from state_management import load_discarded_images, load_catalog_data
import ui_constants

st.set_page_config(
    page_title="Product & Tag Recognizer",
    page_icon="📷",
    layout="wide",    
)

load_discarded_images()
load_catalog_data()

st.write("# Home")
st.write('This is a sample application to work with Product & Tag Recognizer.')
with st.container():
    st.write("## Data Loaded")
    #create three columns with metrics
    col1, col2 = st.columns(2)
    col1.metric(label="Number of Catalog Entries", value= len(st.session_state[ui_constants.STATE_ADDED_BUNDLES_KEY]))
    col2.metric(label="Number of Discarded Images", value= len(st.session_state[ui_constants.STATE_DISCARDED_IMAGES_KEY]))

st.divider()
st.write("## Process overview")
st.image('images/process_overview.png')