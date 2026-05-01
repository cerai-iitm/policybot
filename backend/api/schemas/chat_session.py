# api/schemas/chat_session.py
from pydantic import BaseModel
from datetime import datetime


class ChatSessionCreate(BaseModel):
    notebook_id: str
    title: str | None = None


class ChatSessionResponse(BaseModel):
    id: int
    session_id: str
    notebook_id: str
    title: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChatSessionListResponse(BaseModel):
    sessions: list[ChatSessionResponse]
