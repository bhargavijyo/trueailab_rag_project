from typing import List, Dict
from app.models.database import SessionLocal, ChatHistory
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class MemoryService:
    def __init__(self, limit: int = 5):
        # We store last `limit` message pairs (i.e. 10 messages)
        self.limit = limit * 2

    def add_message(self, session_id: str, role: str, content: str):
        db = SessionLocal()
        try:
            msg = ChatHistory(session_id=session_id, role=role, content=content)
            db.add(msg)
            db.commit()
        except Exception as e:
            logger.error(f"Error saving message to memory: {e}")
        finally:
            db.close()

    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        db = SessionLocal()
        try:
            messages = db.query(ChatHistory).filter(ChatHistory.session_id == session_id).order_by(ChatHistory.timestamp.asc()).all()
            history = [{"role": msg.role, "content": msg.content} for msg in messages[-self.limit:]]
            return history
        finally:
            db.close()
