from constants import RUNS_BUCKET, CONSOLIDATED_FOLDER
from services.data.firestore_service import FirestoreService
from services.gcs_service import load_json_blob 
import constants
from utils import get_image_id

class RunService():
    
    def __init__(self):
        pass

    def get_run_results(self, run_id):
        file_path = run_id + '/'+ CONSOLIDATED_FOLDER + '/final.jsonl'
        result = load_json_blob(RUNS_BUCKET, file_path)
        return result
    
    # Given a  result run will create a list of images
    def image_list(self, run_info):
        image_keys = []
        image_uri = []
        for entry in run_info:
            image_id = entry['imageUri'].split("/")[-2]
            if image_id not in image_keys:
                image_keys.append(image_id)
                image_uri.append(entry['original_image_uri'])
        return list(zip(image_keys,image_uri))
    
    def get_run_results_per_image(self, run_id, filtering_image_id):
        run_results = self.get_run_results(run_id=run_id)
        results = []
        for entry in run_results:
            filename = get_image_id(entry['original_image_uri'])
            if filtering_image_id == filename:
                results.append(entry)
        return results

    def get_run_results_per_image_set(self, run_id, image_set):
        result =[]
        for image in image_set:
            image_id = get_image_id(image)
            result.extend( self.get_run_results_per_image(run_id, image_id))

        return result
    
    # Given a  result run will create a list of images
    def image_list(self, run_info):
        image_keys = []
        image_uri = []
        for entry in run_info:
            image_id = entry['imageUri'].split("/")[-2]
            if image_id not in image_keys:
                image_keys.append(image_id)
                image_uri.append(entry['original_image_uri'])
        return list(zip(image_keys,image_uri))
    
    def image_filename_list(self, run_info):
        image_list = self.image_list(run_info)
        return [x[0] for x in image_list]
    
    def get_run_results(self, run_id):
        file_path = run_id + '/'+ CONSOLIDATED_FOLDER + '/final.jsonl'
        result = load_json_blob(RUNS_BUCKET, file_path)
        return result
