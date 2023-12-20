import csv
import streamlit as st
import utils
import ui_constants
import pandas as pd
from constants import CATALOG_BUCKET, CATALOG_UPDATES_FILEPATH, IMAGE_EXCLUSION_FILEPATH


from gcs_helper import  load_text_blob, upload_dataframe_to_gcs

def create_bundles_dataframe(data):
    temp_data = []
    for entry in data:
        temp_data.append({'Article': entry['article_id'], 'image': utils.transform_html_path(entry['original_image_uri']), 'choose':False})
    # Create the DataFrame
    return pd.DataFrame(temp_data)

def save_catalog(data):
    """ Saves Bundles to GCS storage"""
    # data - the array with the entries for the bundles
    df = create_bundles_dataframe(data)
    upload_dataframe_to_gcs(df, CATALOG_BUCKET, CATALOG_UPDATES_FILEPATH  )

def create_dataframe(data):
    temp_data = []
    for entry in data:
        temp_data.append({'image_uri':entry, 'image': utils.transform_html_path(entry) })
    # Create the DataFrame
    return pd.DataFrame(temp_data)

def save_discarded_images(data): 
    """ Saves discarded images to GCS storage """
    # data - the array with that reprsents the images that are to be removed
    df = create_dataframe(data)
    upload_dataframe_to_gcs(df, CATALOG_BUCKET, IMAGE_EXCLUSION_FILEPATH  )



def load_discarded_images():
    csv_string = load_text_blob(CATALOG_BUCKET, IMAGE_EXCLUSION_FILEPATH)
    data = [row[0] for row in csv.reader(csv_string.splitlines())]
    st.session_state[ui_constants.STATE_DISCARDED_IMAGES_KEY] = data[1:]
    print(f'Loaded {len(data)} discarded images')


def load_catalog_data():
    csv_string = load_text_blob(CATALOG_BUCKET, CATALOG_UPDATES_FILEPATH)
    data = [{'article_id': row[0], 'original_image_uri' : row[1] } for row in csv.reader(csv_string.splitlines())]
    st.session_state[ui_constants.STATE_ADDED_BUNDLES_KEY] = data[1:]
    print(f'Loaded {len(data)} bundles')


