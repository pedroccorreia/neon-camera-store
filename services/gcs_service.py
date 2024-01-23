from google.cloud import storage
import json

def load_jsonl_blob(bucket_name, blob_name):
    """Loads a blob from the bucket."""
    #contains gs:// remove it
    bucket_name = bucket_name.replace('gs://','')

    # Instantiate a Google Cloud Storage client and specify required bucket and file
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)

    raw_data = blob.download_as_text(client=None)
    temp = raw_data.split('\n')

    data = [json.loads(line) for line in temp[:-1]]

    # Download the contents of the blob as a string and then parse it using json.loads() method
    return data

def load_json_blob(bucket_name, blob_name):
    """Loads a blob from the bucket."""
    #contains gs:// remove it
    bucket_name = bucket_name.replace('gs://','')

    # Instantiate a Google Cloud Storage client and specify required bucket and file
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)

    raw_data = blob.download_as_text(client=None)
    
    data = json.loads(raw_data)

    # Download the contents of the blob as a string and then parse it using json.loads() method
    return data

def load_text_blob(bucket_name, blob_name):
    """Loads a blob from the bucket as a string"""
    #contains gs:// remove it
    bucket_name = bucket_name.replace('gs://','')

    # Instantiate a Google Cloud Storage client and specify required bucket and file
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)

    raw_data = blob.download_as_text(client=None)
    


    # Download the contents of the blob as a string and then parse it using json.loads() method
    return raw_data


#create a functions that gives you the files in a given bucket
def list_blobs(bucket_name):
    #contains gs:// remove it
    bucket_name = bucket_name.replace('gs://','')

    """Lists all the blobs in the bucket."""

    storage_client = storage.Client()

    blobs = storage_client.list_blobs(bucket_name)

    return blobs



def list_blobs_prefix(bucket_name, path_prefix, skip_folders=True):
    """Lists all the blobs in the bucket and returns the one that satisfy
    a prefix"""
    #contains gs:// remove it
    bucket_name = bucket_name.replace('gs://','')

    storage_client = storage.Client()

    blobs = storage_client.list_blobs(bucket_name)

    res =[]
    for blob in blobs:

      if(blob.name.startswith(path_prefix)):
        if(skip_folders):
          if(blob.name.endswith('/')):
            continue
        res.append(blob.name)
    return res


def upload_dataframe_to_gcs(df, bucket_name, file_path):
  """
  Writes a Pandas dataframe to a Google Cloud Storage bucket.

  Args:
    df: The Pandas dataframe to be written.
    bucket_name: The name of the GCS bucket.
    file_path: The desired file path within the bucket.

  Returns:
    None
  """
  #contains gs:// remove it
  bucket_name = bucket_name.replace('gs://','')

  client = storage.Client()
  bucket = client.bucket(bucket_name)
  blob = bucket.blob(file_path)
  
  bucket_name = bucket_name.replace('gs://','')
  data = df.to_csv(None, index=False)
  blob.upload_from_string(data)

  print(f"Dataframe successfully written to GCS bucket: gs://{bucket_name}/{file_path}")

def upload_blob_from_memory(bucket_name, contents, destination_blob_name):
    """Uploads a file to the bucket."""

    #contains gs:// remove it
    bucket_name = bucket_name.replace('gs://','')

    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"

    # The contents to upload to the file
    # contents = "these are my contents"

    # The ID of your GCS object
    # destination_blob_name = "storage-object-name"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_string(contents)

def delete_file_from_gcs(bucket_name, file_path):
  """
  Deletes a file from a Google Cloud Storage bucket.

  Args:
    bucket_name: The name of the GCS bucket.
    file_path: The path of the file to be deleted within the bucket.

  Returns:
    None
  """

  bucket_name = bucket_name.replace('gs://','')

  client = storage.Client()
  bucket = client.bucket(bucket_name)
  blob = bucket.blob(file_path)

  blob.delete()

  print(f"File deleted from GCS bucket: gs://{bucket_name}/{file_path}")


def create_run_file(run_bucket, run_id, bucket_name, contents, destination_blob_name):
    """Uploads a file to the bucket."""
    #contains gs:// remove it
    bucket_name = run_bucket.replace('gs://','')

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(run_id+'/'+destination_blob_name)

    blob.upload_from_string(contents)

    print(
        f"{destination_blob_name} with contents {contents} uploaded to {bucket_name}."
    )

def upload_file(bucket_name, contents, destination_blob_name):
    """Uploads a file to the bucket."""
    #contains gs:// remove it
    bucket_name = bucket_name.replace('gs://','')

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_string(contents)


def load_blob(bucket_name, blob_name):
    """Loads a blob from the bucket."""
    #contains gs:// remove it
    bucket_name = bucket_name.replace('gs://','')

    # Instantiate a Google Cloud Storage client and specify required bucket and file
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)

    return blob

def copy_blob(
    bucket_name, blob_name, destination_bucket_name, destination_blob_name,
):
    """Copies a blob from one bucket to another with a new name."""
    # bucket_name = "your-bucket-name"
    # blob_name = "your-object-name"
    # destination_bucket_name = "destination-bucket-name"
    # destination_blob_name = "destination-object-name"

    #contains gs:// remove it
    bucket_name = bucket_name.replace('gs://','')
    destination_bucket_name = destination_bucket_name.replace('gs://','')

    storage_client = storage.Client()

    source_bucket = storage_client.bucket(bucket_name)
    source_blob = source_bucket.blob(blob_name)
    destination_bucket = storage_client.bucket(destination_bucket_name)


    blob_copy = source_bucket.copy_blob(
        source_blob, destination_bucket, destination_blob_name,
    )

    return blob_copy