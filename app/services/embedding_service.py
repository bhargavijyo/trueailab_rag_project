import os
import google.generativeai as genai
from typing import List
from app.utils.logger import setup_logger
from dotenv import load_dotenv

load_dotenv()
logger = setup_logger(__name__)

class EmbeddingService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=api_key)
        self.model = "models/gemini-embedding-001"

    def get_embedding(self, text: str) -> List[float]:
        try:
            result = genai.embed_content(
                model=self.model,
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise e

    def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        try:
            embeddings = []
            for text in texts:
                result = genai.embed_content(
                    model=self.model,
                    content=text,
                    task_type="retrieval_document"
                )
                embeddings.append(result['embedding'])
            return embeddings
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {str(e)}")
            raise e
