import os
import json
import faiss
import numpy as np
from typing import List, Dict, Any, Tuple
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class FaissStore:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.index_path = os.path.join(data_dir, "faiss_index.bin")
        self.metadata_path = os.path.join(data_dir, "metadata.json")
        self.dimension = 3072  # Gemini embedding dimension
        self.index = None
        self.metadata = []
        
        os.makedirs(data_dir, exist_ok=True)
        self.load()

    def build_index(self, embeddings: List[List[float]], metadata: List[Dict[str, Any]]):
        logger.info("Building FAISS index...")
        vectors = np.array(embeddings).astype('float32')
        # Normalize vectors for cosine similarity (Inner Product with normalized vectors)
        faiss.normalize_L2(vectors)
        
        self.index = faiss.IndexFlatIP(self.dimension)
        self.index.add(vectors)
        self.metadata = metadata
        
        self.save()
        logger.info(f"FAISS index built with {self.index.ntotal} vectors.")

    def search(self, query_embedding: List[float], top_k: int = 3, threshold: float = 0.75) -> List[Dict[str, Any]]:
        if self.index is None or self.index.ntotal == 0:
            logger.warning("FAISS index is empty or not loaded.")
            return []
            
        vector = np.array([query_embedding]).astype('float32')
        faiss.normalize_L2(vector)
        
        scores, indices = self.index.search(vector, top_k)
        
        results = []
        for j, i in enumerate(indices[0]):
            if i == -1:
                continue
            score = scores[0][j]
            logger.info(f"Retrieved chunk {i} with similarity score: {score:.4f}")
            if score >= threshold:
                chunk_data = self.metadata[i].copy()
                chunk_data["score"] = float(score)
                results.append(chunk_data)
                
        return results

    def save(self):
        if self.index:
            faiss.write_index(self.index, self.index_path)
            with open(self.metadata_path, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=4)
            logger.info("FAISS index and metadata saved to disk.")

    def load(self):
        if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.metadata_path, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
            logger.info(f"Loaded FAISS index with {self.index.ntotal} vectors.")
        else:
            logger.info("No existing FAISS index found. A new one will be created upon insertion.")
