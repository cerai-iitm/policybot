# api/schemas/pdf.py
from datetime import datetime

from pydantic import BaseModel


class SuggestedQueryResponse(BaseModel):
    """Response model for a single suggested query."""

    query_text: str
    order_index: int

    class Config:
        from_attributes = True


class PDFUploadResponse(BaseModel):
    """PDF upload response - uses stored_filename as identifier."""

    stored_filename: str
    original_filename: str
    # External API should expose notebook_id as the public string (eg "nb_xxx")
    notebook_id: str
    file_path: str
    processing_status: str
    uploaded_at: datetime

    class Config:
        from_attributes = True


class PDFResponse(BaseModel):
    """PDF response with suggested queries - uses stored_filename as identifier."""

    stored_filename: str
    original_filename: str
    # Return the external notebook_id string
    notebook_id: str
    processing_status: str
    summary: str | None = None
    uploaded_at: datetime
    suggested_queries: list[SuggestedQueryResponse] = []

    class Config:
        from_attributes = True


class PDFListResponse(BaseModel):
    notebook_id: str
    pdfs: list[PDFResponse]


class PDFDeleteResponse(BaseModel):
    message: str
    file_deleted: bool
    pdf_record_deleted: bool
