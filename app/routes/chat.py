from fastapi import APIRouter, HTTPException, Depends
from pydantic import ValidationError
from app.models.schemas import ChatRequest, ChatResponse
from app.services.rag_service import RagService
from app.services.retrieval_service import RetrievalService
from app.services.llm_service import LLMService
from app.services.memory_service import MemoryService
from app.services.embedding_service import EmbeddingService
from app.vectorstore.faiss_store import FaissStore
from app.utils.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter()

# Initialize services
embedding_service = EmbeddingService()
vector_store = FaissStore()
retrieval_service = RetrievalService(embedding_service, vector_store)
llm_service = LLMService()
memory_service = MemoryService()
rag_service = RagService(retrieval_service, llm_service, memory_service)

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    if not request.sessionId.strip():
        raise HTTPException(status_code=400, detail="Session ID cannot be empty.")
        
    try:
        reply, tokens, retrieved = rag_service.process_query(request.sessionId, request.message)
        return ChatResponse(
            reply=reply,
            tokensUsed=tokens,
            retrievedChunks=retrieved
        )
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
