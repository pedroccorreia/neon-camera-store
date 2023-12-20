import uuid 
from constants import CATALOG_BUCKET, IMAGE_EXTENSION, PRODUCT_LABELLING_CATEGORIES
  

def transform_html_path(uri):
    return uri.replace("gs://", "https://storage.cloud.google.com/")

def transform_gcs_uri(uri):
    return uri.replace("https://storage.cloud.google.com/", "gs://")

def get_image_id(uri):
    return uri.split('/')[-1].split('.')[0]


def transform_bundle_html_path(bundle):
    bundle['original_image'] = transform_html_path(bundle['original_image'])
    for image in bundle['similar_images']:
        image['image_path'] = transform_html_path(image['image_path'])
    return bundle

def transform_bundle_gcs_uri(bundle):
    bundle['path'] = transform_gcs_uri(bundle['path'])
    bundle['filename'] = transform_gcs_uri(bundle['filename'])
    for image in bundle['similar_images']:
        image['image_path'] = transform_gcs_uri(image['image_path'])
    return bundle


def generate_image_id():
    return uuid.uuid1().int

def transform_bundle_entry_to_catalog( image_path, article_id):
    new_image_uri = CATALOG_BUCKET+'/'+ get_image_id(image_path)+ IMAGE_EXTENSION
    return {'article_id': article_id, 'image_uri' : new_image_uri, 'original_image_uri' : image_path, 'image_id':generate_image_id()}


def transform_bundle_to_catalog( bundle, article_id):
    bundle = transform_bundle_gcs_uri(bundle) 
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
