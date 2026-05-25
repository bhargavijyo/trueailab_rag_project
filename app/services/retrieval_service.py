from typing import List, Dict, Any
from app.services.embedding_service import EmbeddingService
from app.vectorstore.faiss_store import FaissStore
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class RetrievalService:
    def __init__(self, embedding_service: EmbeddingService, vector_store: FaissStore):
        self.embedding_service = embedding_service
        self.vector_store = vector_store

    def retrieve_context(self, query: str, top_k: int = 3, threshold: float = 0.75) -> List[Dict[str, Any]]:
        logger.info(f"Retrieving context for query: {query}")
        query_embedding = self.embedding_service.get_embedding(query)
        
        results = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k,
            threshold=threshold
        )
        
        return results
