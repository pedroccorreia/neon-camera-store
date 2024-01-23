from typing import  List, Optional
from tenacity import retry, stop_after_attempt
from embedding_prediction_client import EmbeddingPredictionClient
import constants
from google.cloud import aiplatform_v1


class MatchingService():

    def __init__(self, 
                 api_endpoint : str = constants.MATCHING_ENGINE_API_ENDPOINT, 
                 index_endpoint : str = constants.MATCHING_ENGINE_INDEX_ENDPOINT, 
                 deployed_index_id:str = constants.MATCHING_ENGINE_DEPLOYED_INDEX_ID):
        # Initialize the client
        self.client = EmbeddingPredictionClient(project=constants.PROJECT_ID)
        self.api_endpoint = api_endpoint
        self.index_endpoint = index_endpoint
        self.deployed_index_id = deployed_index_id
        

    # Use a retry handler in case of failure
    @retry(reraise=True, stop=stop_after_attempt(3))
    def encode_texts_to_embeddings_with_retry(self, text: List[str]) -> List[List[float]]:
        assert len(text) == 1

        try:
            return [self.client.get_embedding(text=text[0], image_file=None).text_embedding]
        except Exception:
            raise RuntimeError("Error getting embedding.")


    def encode_texts_to_embeddings(self, text: List[str]) -> List[Optional[List[float]]]:
        try:
            return self.encode_texts_to_embeddings_with_retry(text=text)
        except Exception:
            return [None for _ in range(len(text))]


    @retry(reraise=True, stop=stop_after_attempt(3))
    def encode_images_to_embeddings_with_retry(self, image_uris: List[str]) -> List[List[float]]:
        assert len(image_uris) == 1

        try:
            return [
                self.client.get_embedding(text=None, image_file=image_uris[0]).image_embedding
            ]
        except Exception as ex:
            print(ex)
            raise RuntimeError("Error getting embedding.")


    def encode_images_to_embeddings(self, image_uris: List[str]) -> List[Optional[List[float]]]:
        try:
            return self.encode_images_to_embeddings_with_retry(image_uris=image_uris)
        except Exception as ex:
            print(ex)
            return [None for _ in range(len(image_uris))]


    def get_matches(self, gcs_uri: str):

        image_embeddings = self.encode_images_to_embeddings([gcs_uri])
        # Set client options
        client_options = {
            "api_endpoint": self.api_endpoint
        }

        vector_search_client = aiplatform_v1.MatchServiceClient(client_options=client_options)
        # Build FindNeighborsRequest object
        datapoint = aiplatform_v1.IndexDatapoint(
        feature_vector=image_embeddings[0]
        )
        query = aiplatform_v1.FindNeighborsRequest.Query(
        datapoint=datapoint,
        # The number of nearest neighbors to be retrieved
        neighbor_count=15
        )
        request = aiplatform_v1.FindNeighborsRequest(
        index_endpoint=self.index_endpoint,
        deployed_index_id=self.deployed_index_id,
        # Request can have multiple queries
        queries=[query],
        return_full_datapoint=False,
        )

        # Execute the request
        response = vector_search_client.find_neighbors(request)

        similarity_results = []
        for neighbors in response.nearest_neighbors:
            for neighbor in neighbors.neighbors:
                similarity_results.append([neighbor.datapoint.datapoint_id.replace("gs://", "https://storage.cloud.google.com/"), neighbor.distance])
    
        return similarity_results


    