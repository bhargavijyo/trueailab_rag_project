import tiktoken
from typing import List, Dict, Any
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class ChunkingService:
    def __init__(self, chunk_size: int = 400, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def chunk_document(self, doc_id: str, title: str, content: str) -> List[Dict[str, Any]]:
        tokens = self.tokenizer.encode(content)
        chunks = []
        start = 0
        chunk_idx = 0
        
        while start < len(tokens):
            end = start + self.chunk_size
            chunk_tokens = tokens[start:end]
            chunk_text = self.tokenizer.decode(chunk_tokens)
            
            chunk = {
                "chunk_id": f"{doc_id}_chunk_{chunk_idx}",
                "document_title": title,
                "source_document": doc_id,
                "chunk_text": chunk_text
            }
            chunks.append(chunk)
            
            start += self.chunk_size - self.chunk_overlap
            chunk_idx += 1
            
        return chunks

    def process_documents(self, documents: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        all_chunks = []
        for i, doc in enumerate(documents):
            title = doc.get("title", f"Document {i}")
            content = doc.get("content", "")
            doc_id = f"doc_{i}"
            doc_chunks = self.chunk_document(doc_id, title, content)
            all_chunks.extend(doc_chunks)
        
        logger.info(f"Generated {len(all_chunks)} chunks from {len(documents)} documents.")
        return all_chunks
