import os
from typing import List, Optional
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore, FastEmbedSparse, RetrievalMode
from langchain.docstore.document import Document
from backend.src.config import ModelConfig
from qdrant_client import QdrantClient

class RetrievalEngine:
    """Handles Hybrid Search and Reranking using Qdrant."""

    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name=ModelConfig.EMBEDDING_MODEL)
        self.sparse_embeddings = FastEmbedSparse(model_name="Qdrant/bm25")
        
        self.host = ModelConfig.QDRANT_HOST
        self.port = 6333
        self.timeout = 120.0
        
        # Configure the Qdrant Client explicitly with host, port, and timeout
        self.client = QdrantClient(host=self.host, port=self.port, timeout=self.timeout)
        self.qdrant_url = f"http://{self.host}:{self.port}"
        self.qdrant_store: Optional[QdrantVectorStore] = None

    def initialize_vector_store(self, text_chunks: Optional[List[Document]], save_path: str):
        """
        Initializes or connects to a Qdrant collection.
        'save_path' here represents the collection name from VectorStoreManager.
        """
        collection_name = save_path
        
        # If chunks exist, we ingest them
        if text_chunks:
            self.qdrant_store = QdrantVectorStore.from_documents(
                text_chunks,
                embedding=self.embeddings,
                sparse_embedding=self.sparse_embeddings,
                url=self.qdrant_url,
                collection_name=collection_name,
                retrieval_mode=RetrievalMode.HYBRID,
                timeout=120.0
            )
        else:
            # We are just connecting to query an existing collection
            self.qdrant_store = QdrantVectorStore.from_existing_collection(
                embedding=self.embeddings,
                sparse_embedding=self.sparse_embeddings,
                url=self.qdrant_url,
                collection_name=collection_name,
                retrieval_mode=RetrievalMode.HYBRID,
                timeout=120.0
            )

    def get_hybrid_retriever(self):
        """Returns the Qdrant native hybrid retriever."""
        if not self.qdrant_store:
            raise ValueError("Retrieval engine not initialized. Please call initialize_vector_store first.")
        
        return self.qdrant_store.as_retriever(search_kwargs={"k": 5})
