# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# install requirements
pip install -r requirements.txt 

# export path to service account key 
export  GOOGLE_APPLICATION_CREDENTIALS

# run the application
streamlit run home.py 

# Example of jsonl files

JSONL object with:
- original_image: gcs_uri for the originator of the bundles
- similar_images: array of matches
    - image_path: gcs_uri
    - similarity_score: confidence level of the similarity between the images


# Deploying to Cloud Run
## Build the container
```
docker build -t eu.gcr.io/neon-camera-403606/product_labelling:v1 .
```
Once that is done push it to the Artifact Registry: 

```
docker push eu.gcr.io/neon-camera-403606/product_labelling:v1
```

# Push new version of the container
```
gcloud run deploy product-labelling-open \
--image=eu.gcr.io/neon-camera-403606/product_labelling@sha256:bd10a0cf30dd93c24510ed07b4ad79ef0b7207323b738d017eea7ce971aaacb6 \
--region=us-central1 \
--project=neon-camera-403606 \
 && gcloud run services update-traffic product-labelling-open --to-latest --region=us-central1

```