from typing import Tuple, Dict, Any
from app.services.retrieval_service import RetrievalService
from app.services.llm_service import LLMService
from app.services.memory_service import MemoryService
from app.prompts.prompt_template import SYSTEM_PROMPT
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class RagService:
    def __init__(self, retrieval_service: RetrievalService, llm_service: LLMService, memory_service: MemoryService):
        self.retrieval_service = retrieval_service
        self.llm_service = llm_service
        self.memory_service = memory_service

    def process_query(self, session_id: str, query: str) -> Tuple[str, int, int]:
        # 1. Retrieve relevant chunks
        chunks = self.retrieval_service.retrieve_context(query)
        retrieved_count = len(chunks)
        
        if retrieved_count == 0:
            reply = "I could not find enough information in the knowledge base to answer this question."
            # We still record this interaction
            self.memory_service.add_message(session_id, "user", query)
            self.memory_service.add_message(session_id, "assistant", reply)
            return reply, 0, 0
            
        # 2. Build context
        context_texts = [f"--- Document: {chunk['document_title']} ---\n{chunk['chunk_text']}" for chunk in chunks]
        context_str = "\n\n".join(context_texts)
        
        # 3. Construct messages for LLM
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        # Add conversation history
        history = self.memory_service.get_history(session_id)
        messages.extend(history)
        
        # Add current user prompt with context
        user_prompt = f"Context:\n{context_str}\n\nQuestion:\n{query}"
        messages.append({"role": "user", "content": user_prompt})
        
        # 4. Generate response
        reply, tokens_used = self.llm_service.generate_response(messages)
        
        # 5. Save to memory
        self.memory_service.add_message(session_id, "user", query)
        self.memory_service.add_message(session_id, "assistant", reply)
        
        return reply, tokens_used, retrieved_count
