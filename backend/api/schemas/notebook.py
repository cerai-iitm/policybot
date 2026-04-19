# api/schemas/notebook.py
from pydantic import BaseModel
from datetime import datetime


class NotebookCreate(BaseModel):
    title: str
    description: str | None = None


class NotebookResponse(BaseModel):
    id: int
    notebook_id: str
    title: str
    description: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class NotebookListResponse(BaseModel):
    notebooks: list[NotebookResponse]


class NotebookUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
