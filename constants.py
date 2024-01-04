# Retrieve the project number
PROJECT_NUMBER = "1044073708529"
PROJECT_ID = "neon-camera-403606"
REGION="us-central1"
BUCKET_URI = f"gs://{PROJECT_ID}-intermediate" 
INPUT_BUCKET = "gs://neon-camera-403606-classification"
BUNDLE_FILENAME = "similarity_results.jsonl"   

VPC_NETWORK = "vertex"
VPC_NETWORK_FULL = "projects/{}/global/networks/{}".format(PROJECT_NUMBER, VPC_NETWORK)

# INDEX_ENDPOINT_ID ="projects/1044073708529/locations/us-central1/indexEndpoints/8453612742341820416"
# INDEX_ENDPOINT_ID ="projects/1044073708529/locations/us-central1/indexEndpoints/6564352698659897344"
INDEX_ENDPOINT_ID = "projects/1044073708529/locations/us-central1/indexEndpoints/974541136162979840"
DEPLOYED_INDEX_ID = "test_1702008356954"


# similarities constantns
API_IMAGES_PER_SECOND = 2
# Define number of neighbors to return
NUM_NEIGHBORS = 15



# Run Constants
API_ENDPOINT='visionai.googleapis.com'
CATALOG_ID='neon-camera-catalog-demo'

CATALOG_ID='neon-camera-catalog-gregory-hill-demo'
ENDPOINT_ID='002'

RUN_INPUT_BUCKET='gs://neon-camera-403606-input'
RUN_OUTPUT_BUCKET='gs://neon-camera-403606-output'

RUNS_BUCKET='gs://neon-camera-403606-runs'
RECOGNITION_FOLDER='recognition'
CONSOLIDATED_FOLDER='consolidated'

IMAGE_LIST_FILENAME='input_files.txt'

IMAGE_EXTENSION ='.jpg'

CATALOG_BUCKET ='gs://neon-camera-403606-catalog'

CATALOG_FILEPATH ='data/product_catalog.csv'
CATALOG_UPDATES_FILEPATH = 'updates/product_images.csv'
IMAGE_EXCLUSION_FILEPATH = 'exclude/discarded_images.csv'

PRODUCT_LABELLING_CATEGORIES = ['None', 'Bread', 'Cofee', 'Meat', 'Soft Drinks', 'Tea']

#Data Constants
COLLECTION_DISCARDED = 'discarded'
COLLECTION_CATALOG = 'catalog'


