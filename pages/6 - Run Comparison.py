import streamlit as st
import pandas as pd
from streamlit_image_comparison import image_comparison

from services.data.firestore_service import FirestoreService
from services.runs.run_service import RunService
import ui_constants
from utils import run_recognition_metrics

#init the data service
data_service = FirestoreService()
run_service = RunService()


# set page config
st.set_page_config(page_title="Image-Comparison Example",layout="wide",)

st.write('Functionality being developed')

# def get_run_list_dataframe():
#     # Create a Pandas DataFrame with firestore data
#     columns = ['id', 'catalog', 'category', 'observations', 'run_date', 'visible']

#     data = data_service.get_recognition_runs()
#     return pd.DataFrame(data,columns=columns)

@st.cache_data
def get_run_data():
    data = data_service.get_recognition_runs()
    run_list = [row['id'] for row in data]
    return run_list

@st.cache_data
def get_run_results(run_id):
    return run_service.get_run_results(run_id)


def handle_comparison(first_option, second_run_option):
    st.session_state['allow_compare'] = True
    st.session_state['first_option'] = first_option
    st.session_state['second_run_option'] = second_run_option


def compare_runs(first_option, second_run_option):
    #First Run Data & Metrics
    print(f'Getting First Run data')
    first_run_results = get_run_results(first_option)

    first_run_image_info = run_service.image_list(first_run_results)
    first_run_image_set = [row[1] for row in first_run_image_info]
    first_run_results = run_service.get_run_results_per_image_set(first_option, first_run_image_set)
    first_run_df = run_recognition_metrics(first_run_results)

    first_run_filtered_df = first_run_df[first_run_df['Products'] == 'No Product Matched']
    first_run_num_no_products_found = first_run_filtered_df.sum()['Percentage of total']
    first_run_unique_products = first_run_df['Products'].nunique()

    #Second Run Data & Metrics
    print(f'Getting Second Run data')
    second_run_results = get_run_results(second_run_option)
    second_run_image_info = run_service.image_list(second_run_results)
    second_run_image_set = [row[1] for row in second_run_image_info]
    second_run_results = run_service.get_run_results_per_image_set(second_run_option, second_run_image_set)
    second_run_df = run_recognition_metrics(second_run_results)

    second_run_filtered_df = second_run_df[second_run_df['Products'] == 'No Product Matched']
    second_run_num_no_products_found = second_run_filtered_df.sum()['Percentage of total']
    second_run_unique_products = second_run_df['Products'].nunique()

    #Merge Data
    print(f'Merging Data')
    merged_df = pd.merge(first_run_df, second_run_df, on='Products', how='outer', suffixes=('_first', '_second'))
    merged_df = merged_df[['Products', 'Facings_first', 'Facings_second']]
    merged_df['Facings_first'] = merged_df['Facings_first'].replace(to_replace='None', value='0')
    merged_df['Facings_second'] = merged_df['Facings_second'].replace(to_replace='None', value='0')

    merged_df['delta'] =  merged_df['Facings_second'].sub(merged_df['Facings_first'], fill_value=0) #merged_df['Facings_second'] - merged_df['Facings_first']
      
    st.write("Metrics")
    with st.container(border=2):
        cols = st.columns(4)
        cols[0].metric(label="Images", value=len(second_run_image_set), delta=len(second_run_image_set)-len(first_run_image_set))
        cols[1].metric(label="Product Facings", value=len(second_run_results), delta=len(second_run_results)-len(first_run_results))
        cols[2].metric(label="Missing Products %", value=second_run_num_no_products_found, delta=second_run_num_no_products_found-first_run_num_no_products_found)
        cols[3].metric(label="Unique Products", value=second_run_unique_products, delta=second_run_unique_products-first_run_unique_products)

    st.write("Comparison")
    with st.container(border=2):
        st.dataframe(data=merged_df, use_container_width=True, hide_index=True)
   
    st.write("Run Details")
    cols = st.columns(2)
    with cols[0].expander(f'{first_option}', expanded=False):
        metrics_cols = st.columns(4)
        metrics_cols[0].metric('Images', len(first_run_image_set))
        metrics_cols[1].metric('Product Facings', len(first_run_results))
        metrics_cols[2].metric('Missing Products %', first_run_num_no_products_found)
        metrics_cols[3].metric('Unique Products', first_run_unique_products if first_run_num_no_products_found == 0 else first_run_unique_products - 1)
        st.write("Products")
        st.dataframe(data=first_run_df, use_container_width=True, hide_index=True)
    with cols[1].expander(f'{second_run_option}', expanded=False):
        metrics_cols = st.columns(4)
        metrics_cols[0].metric('Images', len(second_run_image_set))
        metrics_cols[1].metric('Product Facings', len(second_run_results))
        metrics_cols[2].metric('Missing Products %', second_run_num_no_products_found)
        metrics_cols[3].metric('Unique Products', second_run_unique_products if second_run_num_no_products_found == 0 else second_run_unique_products - 1)
        st.write("Products")
        st.dataframe(data=second_run_df, use_container_width=True, hide_index=True)


# Main

with st.container():
    # get run list
    run_list = get_run_data()

    with st.container():
        cols = st.columns([2,1,2,1,1])
        first_option = cols[0].selectbox(
            'Initial Run',
            run_list)
        second_run_option = cols[2].selectbox(
            'Second Run',
            run_list)
        
        cols[4].button('Compare', on_click=handle_comparison, args=(first_option, second_run_option))
    
    if 'allow_compare' not in st.session_state:
       st.write('choose your runs')
    else:
        if st.session_state['allow_compare']:
            compare_runs(first_option, second_run_option)


        

    