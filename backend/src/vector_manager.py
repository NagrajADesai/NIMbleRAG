import os
import requests
from typing import List
from qdrant_client import QdrantClient
from backend.src.config import AppConfig, ModelConfig

class VectorStoreManager:
    """Manages collections in Qdrant (Docker)."""

    def __init__(self):
        # We assume Qdrant is running locally
        self.host = ModelConfig.QDRANT_HOST
        self.port = 6333
        self.timeout = 120.0
        self.client = QdrantClient(host=self.host, port=self.port, timeout=self.timeout)

    def list_dbs(self) -> List[str]:
        """Returns a list of available Qdrant collections."""
        try:
            collections_response = self.client.get_collections()
            return sorted([c.name for c in collections_response.collections])
        except Exception as e:
            print(f"Error connecting to Qdrant: {e}")
            return []

    def get_db_path(self, db_name: str) -> str:
        """For Qdrant REST API, the 'path' is just the collection name string for reference."""
        return db_name

    def create_db_dir(self, db_name: str) -> str:
        """We no longer create local directories. Just return the name."""
        return db_name
    
    def delete_db(self, db_name: str):
        """Deletes a Qdrant collection."""
        try:
            self.client.delete_collection(collection_name=db_name)
        except Exception as e:
            print(f"Error deleting collection {db_name}: {e}")
