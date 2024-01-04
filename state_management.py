import csv
import streamlit as st
import utils
import pandas as pd
from constants import CATALOG_BUCKET, CATALOG_UPDATES_FILEPATH, IMAGE_EXCLUSION_FILEPATH


from gcs_helper import  load_text_blob, upload_dataframe_to_gcs

def create_bundles_dataframe(data):
    temp_data = []
    for entry in data:
        temp_data.append({'Article': entry['article_id'], 'image': utils.transform_html_path(entry['original_image_uri']), 'choose':False})
    # Create the DataFrame
    return pd.DataFrame(temp_data)

def create_dataframe(data):
    temp_data = []
    for entry in data:
        temp_data.append({'image_uri':entry, 'image': utils.transform_html_path(entry) })
    # Create the DataFrame
    return pd.DataFrame(temp_data)

