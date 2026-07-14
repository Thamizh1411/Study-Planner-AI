from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class ChatRequest(BaseModel):
    topic_title: str
    question: str
    chat_history: Optional[List[Dict[str, str]]] = []

class ChatResponse(BaseModel):
    answer: str

class OCRResponse(BaseModel):
    extracted_text: str
    summary: str
    quiz: List[Dict[str, Any]]

class RAGQueryRequest(BaseModel):
    query: str

class RAGQueryResponse(BaseModel):
    answer: str
    sources: List[str]
