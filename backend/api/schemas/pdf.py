# api/schemas/pdf.py
from pydantic import BaseModel
from datetime import datetime


class PDFUploadResponse(BaseModel):
    pdf_id: int
    original_filename: str
    stored_filename: str
    # External API should expose notebook_id as the public string (eg "nb_xxx")
    notebook_id: str
    file_path: str
    processing_status: str
    uploaded_at: datetime

    class Config:
        from_attributes = True


class PDFResponse(BaseModel):
    id: int
    original_filename: str
    stored_filename: str
    # Return the external notebook_id string
    notebook_id: str
    processing_status: str
    summary: str | None = None
    uploaded_at: datetime

    class Config:
        from_attributes = True


class PDFListResponse(BaseModel):
    notebook_id: str
    pdfs: list[PDFResponse]


class PDFDeleteResponse(BaseModel):
    message: str
    file_deleted: bool
    pdf_record_deleted: bool
