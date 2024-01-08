# Load environment dependent variables from yaml file
import yaml
with open('config.yaml', 'r') as file:
    config_info = yaml.safe_load(file)

# Retrieve the project number
PROJECT_NUMBER = config_info['project']['project_number']
PROJECT_ID = config_info['project']['project_id']
REGION= config_info['project']['region']
BUCKET_URI = f"gs://{PROJECT_ID}-intermediate" 
INPUT_BUCKET = f"gs://{PROJECT_ID}-classification"
BUNDLE_FILENAME = config_info['recognition']['bundle_filename']



# Product recognition - TODO: only required if we are doing product recognition / image similarity
INDEX_ENDPOINT_ID = "projects/1044073708529/locations/us-central1/indexEndpoints/974541136162979840"
DEPLOYED_INDEX_ID = "test_1702008356954"
CATALOG_ID=config_info['recognition']['catalog_id']
ENDPOINT_ID = config_info['recognition']['endpoint_id']


# similarities constantns
API_IMAGES_PER_SECOND = 2
# Define number of neighbors to return
NUM_NEIGHBORS = 15

# Run Constants
API_ENDPOINT='visionai.googleapis.com'

RUN_INPUT_BUCKET=f'gs://{PROJECT_ID}-input'
RUN_OUTPUT_BUCKET=f'gs://{PROJECT_ID}-output'

RUNS_BUCKET=f'gs://{PROJECT_ID}-runs'
RECOGNITION_FOLDER='recognition'
CONSOLIDATED_FOLDER='consolidated'

IMAGE_LIST_FILENAME='input_files.txt'

IMAGE_EXTENSION ='.jpg'

CATALOG_BUCKET =f'gs://{PROJECT_ID}-catalog'
CATALOG_FILEPATH =f'{CATALOG_BUCKET}/product_catalog.csv'

PRODUCT_LABELLING_CATEGORIES = config_info['recognition']['categories']


#Firestore Constants
COLLECTION_DISCARDED = 'discarded'
COLLECTION_CATALOG = 'catalog'


