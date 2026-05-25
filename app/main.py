import json
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import chat
from app.models.database import init_db
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.vectorstore.faiss_store import FaissStore
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

app = FastAPI(title="RAG Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up API...")
    init_db()
    
    # Check if index exists, otherwise build it
    data_dir = "data"
    docs_path = os.path.join(data_dir, "docs.json")
    index_path = os.path.join(data_dir, "faiss_index.bin")
    
    if not os.path.exists(index_path) and os.path.exists(docs_path):
        logger.info("FAISS index not found. Building index from docs.json...")
        with open(docs_path, 'r', encoding='utf-8') as f:
            documents = json.load(f)
            
        chunking_service = ChunkingService()
        chunks = chunking_service.process_documents(documents)
        
        texts = [chunk["chunk_text"] for chunk in chunks]
        
        embedding_service = EmbeddingService()
        
        # Batching embeddings for API limits
        embeddings = []
        batch_size = 50
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]
            batch_embeddings = embedding_service.get_embeddings_batch(batch_texts)
            embeddings.extend(batch_embeddings)
            
        store = FaissStore(data_dir=data_dir)
        store.build_index(embeddings, chunks)
        logger.info("Index building completed.")

@app.get("/health")
def health_check():
    return {"status": "healthy"}
