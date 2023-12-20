# go to the folder start the venv
source /Users/pcorreia/dev/product_image/.venv/bin/activate

# install requirements
pip install -r requirements.txt 

# export path to service account key 
export  GOOGLE_APPLICATION_CREDENTIALS="secrets/credentials.json"

# run the application
streamlit run home.py 


# Example of jsonl files

JSONL object with:
- original_image: gcs_uri for the originator of the bundles
- similar_images: array of matches
    - image_path: gcs_uri
    - similarity_score: confidence level of the similarity between the images