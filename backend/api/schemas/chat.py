# api/schemas/chat.py
from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class ChatQueryRequest(BaseModel):
    query: str
    # Optional: if provided, use specific session; otherwise use active session
    session_id: str | None = None
    # External API should pass notebook_id as the public string (eg "nb_xxx")
    notebook_id: str
    # Use stored_filenames (UUID strings) instead of internal IDs
    stored_filenames: list[str] | None = None


class QueryClassification(BaseModel):
    query_type: Literal["conversational", "rag_question"]
    conversational_response: str | None = None


class HYDEQueries(BaseModel):
    hyde_answer: str
    rewritten_queries: list[str]


class ChatMessageResponse(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class ChatHistoryResponse(BaseModel):
    session_id: str
    messages: list[ChatMessageResponse]


class ChatChunkResponse(BaseModel):
    chunk: str


class ChatDoneResponse(BaseModel):
    done: bool


class ConversationalResponse(BaseModel):
    response: str
    query_type: Literal["conversational"] = "conversational"
    context_chunks: list = []


class RAGResponse(BaseModel):
    query_type: Literal["rag_question"] = "rag_question"
