from services.data.data_service import DataService
import constants
import utils
from google.cloud import firestore


class FirestoreService(DataService):
    

    def __init__(self):
        self.db = firestore.Client(project=constants.PROJECT_ID)

    def has_discarded(self) -> bool:
        # checks if there are any entries in the discarded collection
        return len(self.db.collection(constants.COLLECTION_DISCARDED).get()) > 0
    
    def discard_length(self):
        # returns the number of entries in the discarded collection
        return len(self.db.collection(constants.COLLECTION_DISCARDED).get())


    def add_discarded(self, image_uri):
        # get the image id based on image_uri
        image_id = utils.get_image_id(image_uri=image_uri)
        # add the entry to the discarded collection
        entry_ref = self.db.collection(constants.COLLECTION_DISCARDED).document(image_id)
        entry_ref.set({"image_uri" : image_uri})

        return entry_ref
    
    def remove_discarded(self, image_uri):
        # get the image id based on image_uri
        image_id = utils.get_image_id(image_uri=image_uri)

        entry_ref = self.db.collection(constants.COLLECTION_DISCARDED).document(image_id)
        #get entry key
        entry_key = entry_ref.get().id
        #delete entry
        entry_ref.delete()

        return entry_key
    
    def get_discarded(self):
        #return all entries in the discarded collection and return it
        entries = self.db.collection(constants.COLLECTION_DISCARDED).stream()
        discarded = []
        for entry in entries:
            discarded.append(entry.to_dict())
        #return the discarded
        return discarded
    
    def get_discarded_uris(self):
        #return all entries in the discarded collection and return it
        entries = self.db.collection(constants.COLLECTION_DISCARDED).stream()
        discarded = []
        for entry in entries:
            discarded.append(entry.get("image_uri"))
        #return the discarded
        return discarded
    
    def contains_discarded(self, image_uri):
        # get the image id based on image_uri
        image_id = utils.get_image_id(image_uri=image_uri)
        # check if the discarded collection has a matching entry
        entry_ref = self.db.collection(constants.COLLECTION_DISCARDED).document(image_id).get()
        return entry_ref.exists
        
    
    def get_image_id_from_run(self, image_uri):
        """Extracts the image ID from a given string, removing the extension."""
        tokens = image_uri.split('/')
        filename = tokens[-2]+'-'+tokens[-1]
        filename = filename.split('.')[0]
        return filename
    
    # {'article_id': article_id, 'image_uri' : new_image_uri, 'original_image_uri' : image_path}
    def get_catalog(self):
        # get the catalog entries 
        entries = self.db.collection(constants.COLLECTION_CATALOG).stream()
        catalog = []
        for entry in entries:
            catalog.append(entry.to_dict())
        #return the catalog
        return catalog
    
    def get_catalog_uris(self):
        #return all entries in the catalog collection and return it
        entries = self.db.collection(constants.COLLECTION_CATALOG).stream()
        catalog = []
        for entry in entries:
            catalog.append(entry.get("original_image_uri"))
        #return the discarded
        return catalog
    
    def add_catalog(self, catalog_entry, source):
        # get the image id based on image_uri
        image_id = utils.get_image_id(image_uri=catalog_entry['original_image_uri'])
        # add the entry to the catalog collection
        entry_ref = self.db.collection(constants.COLLECTION_CATALOG).document(image_id)
        # convert numpy to int
        catalog_entry['article_id'] = catalog_entry['article_id'].item()
        catalog_entry['source'] = source
        entry_ref.set(catalog_entry)

        return entry_ref
    
    def add_catalog_entries(self, catalog_entries, source = constants.LABELLING_SOURCE_BUNDLES):
        '''
        Adds a list of catalog entries to the catalog collection
        '''
        added_keys =[]
        for entry in catalog_entries:
            added_keys.append(self.add_catalog(entry, source))
        return added_keys
        
    
    def remove_catalog(self, image_uri):
        # get the image id based on image_uri
        image_id = utils.get_image_id(image_uri=image_uri)

        entry_ref = self.db.collection(constants.COLLECTION_CATALOG).document(image_id)
        #get entry key
        entry_key = entry_ref.get().id
        #delete entry
        entry_ref.delete()
        return entry_key
    
    def contains_catalog(self, image_uri):
        # get the image id based on image_uri
        image_id = utils.get_image_id(image_uri=image_uri)
        # check if the catalog collection has a matching entry
        entry_ref = self.db.collection(constants.COLLECTION_CATALOG).document(image_id).get()
        return entry_ref.exists
    
    def has_catalog(self) -> bool:
        # checks if there are any entries in the catalog collection
        return len(self.db.collection(constants.COLLECTION_CATALOG).get()) > 0

    def catalog_length(self):
        return len(self.db.collection(constants.COLLECTION_CATALOG).get())
    
    def get_recognition_runs(self, filter_visible = False):
        entries = self.db.collection(constants.COLLECTION_RUNS).stream()
        result = []
        for entry in entries:
            if filter_visible:
                #only add if visible
                if entry.get("visible"):
                    result.append(entry.to_dict())
            else: 
                #add it regardless of visibility status
                result.append(entry.to_dict())
        
        return result
        
        
        
        
        