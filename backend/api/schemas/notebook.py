# api/schemas/notebook.py
from pydantic import BaseModel
from datetime import datetime


class NotebookCreate(BaseModel):
    title: str
    description: str | None = None


class NotebookTitle(BaseModel):
    title: str


class NotebookResponse(BaseModel):
    id: int
    notebook_id: str
    title: str
    description: str | None
    created_at: datetime
    processed_pdf_count: int = 0

    class Config:
        from_attributes = True


class NotebookListResponse(BaseModel):
    notebooks: list[NotebookResponse]


class NotebookUpdate(BaseModel):
    title: str | None = None
    description: str | None = None


class PDFDetailItem(BaseModel):
    pdf_id: str
    filename: str
    summary: str | None = None
    suggested_queries: list[str] = []

    class Config:
        from_attributes = True


class PDFDetailsRequest(BaseModel):
    notebook_id: str
    pdf_ids: list[str] | None = None


class PDFDetailsResponse(BaseModel):
    pdfs: list[PDFDetailItem]
