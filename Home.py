import streamlit as st
from services.data.firestore_service import FirestoreService

data_service = FirestoreService()

st.set_page_config(
    page_title="Product & Tag Recognizer",
    page_icon="📷",
    layout="wide",    
)

st.write("# Home")
st.write('This is a sample application to work with Product & Tag Recognizer.')
with st.container():
    st.write("## Data Loaded")
    #create three columns with metrics
    col1, col2 = st.columns(2)
    col1.metric(label="Number of Catalog Entries", value= data_service.catalog_length())
    col2.metric(label="Number of Discarded Images", value= data_service.discard_length())

st.divider()
st.write("## Process overview")
st.image('images/process_overview.png')