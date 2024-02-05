from collections import Counter
import os
import uuid 
from constants import CATALOG_BUCKET, IMAGE_EXTENSION, PRODUCT_LABELLING_CATEGORIES
import pandas as pd
import utils
  

def transform_html_path(uri):
    return uri.replace("gs://", "https://storage.cloud.google.com/")

def transform_gcs_uri(uri):
    return uri.replace("https://storage.cloud.google.com/", "gs://")

def get_image_id(image_uri):
        """Extracts the image ID from a given string, removing the extension."""
        base_filename = os.path.basename(image_uri)  # Get the base filename
        filename, extension = os.path.splitext(base_filename)  # Extract filename
        return filename
    

def generate_image_id():
    return uuid.uuid1().int

def transform_bundle_entry_to_catalog( image_path, article_id):
    new_image_uri = CATALOG_BUCKET+'/'+ utils.get_image_id(image_path)+ IMAGE_EXTENSION
    return {'article_id': article_id, 'image_uri' : new_image_uri, 'original_image_uri' : image_path}


def transform_bundle_to_catalog( bundle, article_id):
    bundle = utils.transform_bundle_gcs_uri(bundle) 
    results = []

    #append origional 
    entry = transform_bundle_entry_to_catalog( bundle['path'], article_id)
    results.append(entry)

    #append similar images
    for similar_image in bundle['similar_images']:
        entry = transform_bundle_entry_to_catalog( similar_image['image_path'], article_id)
        results.append(entry)
    return results


def category_filter_selected_index(category):
    for index, entry in enumerate( PRODUCT_LABELLING_CATEGORIES):
        print(f'looking for {category} in entry {entry} index {index}')
        if(entry == category):
            return index
        


# unique products and their product facings
# add no products identfied and their product facings
def run_recognition_metrics(run_results):
    articles = []
    for result in run_results:
        if (len(result['productRecognitionAnnotations'][0]['recognitionResults']) == 0):
            articles.append('No Product Matched')
        else:
            #assumes the first entry with the highest confidence is the one shown
            prod_data = result['productRecognitionAnnotations'][0]['recognitionResults'][0]['productMetadata']
            articles.append(prod_data['title'])
            
    # count different products
    # Count the occurrences of each article
    article_counts = Counter(articles)

    # Create a list of unique articles and their counts
    unique_articles = [(article, count) for article, count in article_counts.items()]

    # create the pandas dataframe
    result = pd.DataFrame(data=unique_articles, columns=['Products', 'Facings']).sort_values(by='Facings', ascending=False)

    result['Percentage of total'] = round((result['Facings'] / result['Facings'].sum()) * 100)
    return result

    

    
