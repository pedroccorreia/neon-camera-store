```python
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
``` 

# Pre-requisite

## Data format

JSONL object with:
- original_image: gcs_uri for the originator of the bundles
- similar_images: array of matches
    - image_path: gcs_uri
    - similarity_score: confidence level of the similarity between the images

# Testing the application locally

## install requirements

```shell

pip install -r requirements.txt 

```

## export path to service account key 

```shell

export  GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json


```

## Run the application

```shell

streamlit run home.py 

```

A new browser is opened in the home page.

# Deploying to Cloud Run

To build a container and deploy it to cloud run we will need to: 

1. Create your environment dependent config file.
2. Build the container.
3. Push the container to Artifact Registry.
4. Deploy the container to Cloud Run.


## Edit your environment dependent constants

Create a config.yaml file at the root of the project that contains the following environment dependent info. Create one based on the example given: sample_config.


## Environment variables

```shell

export PROJECT_IDENTIFIER='neon-camera-403606'
export CONTAINER_VERSION='v3.3'
export CONTAINER_NAME='product_labelling'
export IMAGE_URI=us.gcr.io/$PROJECT_IDENTIFIER/$CONTAINER_NAME:$CONTAINER_VERSION
export REGION='us-central1'

```

## Build the container
```shell

docker build -t $IMAGE_URI .

```
Once that is done push it to the Artifact Registry: 

```shell

docker push $IMAGE_URI

```

# Push new version of the container

```shell
export CLOUDRUN_SERVICE=product-labelling-open
```

```shell

gcloud run deploy $CLOUDRUN_SERVICE \
--image=us.gcr.io/$PROJECT_IDENTIFIER/$CONTAINER_NAME:$CONTAINER_VERSION \
--region=$REGION \
--project=$PROJECT_IDENTIFIER \
 && gcloud run services update-traffic $CLOUDRUN_SERVICE --to-latest --region=$REGION
 
```