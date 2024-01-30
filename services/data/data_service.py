#Abstract class that allows to connect to a firestore database and reads and writes discarded images
from abc import abstractmethod

"""
    Abstract class that contains all data operations done in the product & tag recognizer
"""
class DataService():
    
    @abstractmethod
    def get_catalog(self):
        """Gets all entries in a catalog"""
        pass

    @abstractmethod
    def get_discarded(self):
        """Retrieves discarded images from the data source."""
        pass

    @abstractmethod
    def add_discarded(self, image_uri):
        """Adds a discarded image to the data source."""
        pass

    @abstractmethod
    def remove_discarded(self, image_uri):
        """Removes a discarded image from the data source."""
        pass

    @abstractmethod
    def contains_discarded(self, image_uri):
        """Checks if a discarded image is in the data source."""
        pass

    @abstractmethod
    def contains_catalog(self, catalog_entry):
        """Checks if a catalog image is in the data source."""
        pass


    @abstractmethod
    def add_catalog(self, catalog_entry, source):
        """Adds a catalog image to the data source."""
        pass

    @abstractmethod
    def remove_catalog(self, catalog_entry):
        """Removes a catalog image from the data source."""

    @abstractmethod
    def get_recognition_runs(self):
        """Shows all recognition runs"""