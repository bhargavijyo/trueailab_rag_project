from pydantic import BaseModel, Field
from typing import List, Optional

class ChatRequest(BaseModel):
    sessionId: str
    message: str

class ChatResponse(BaseModel):
    reply: str
    tokensUsed: int
    retrievedChunks: int

class UserCreate(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
