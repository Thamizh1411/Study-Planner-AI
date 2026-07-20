from typing import Any

from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    topic_title: str
    question: str
    chat_history: list[dict[str, str]] = Field(default_factory=list)

class ChatResponse(BaseModel):
    answer: str

class OCRResponse(BaseModel):
    extracted_text: str
    summary: str
    quiz: list[dict[str, Any]]

class RAGQueryRequest(BaseModel):
    query: str

class RAGQueryResponse(BaseModel):
    answer: str
    sources: list[str]
