"""Pydantic schemas for PDF router responses."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class PDFUploadResponse(BaseModel):
    """Response model for PDF upload endpoint."""

    filename: str = Field(
        ..., example="document.pdf", description="Name of the uploaded file"
    )
    notebook: str = Field(..., example="My Notebook", description="Notebook name")
    notebook_id: str = Field(
        ..., example="nb_a1b2c3d4", description="Unique notebook identifier"
    )
    pdf_id: int = Field(..., example=1, description="Database ID of the PDF record")
    processing_state: str = Field(
        ...,
        example="uploaded",
        description="Current processing status: uploaded, processing, embeddings_complete, summary_generation, or complete",
    )
    file_path: str = Field(
        ..., example="nb_a1b2c3d4/document.pdf", description="Relative path to the file"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "filename": "document.pdf",
                "notebook": "My Notebook",
                "notebook_id": "nb_a1b2c3d4",
                "pdf_id": 1,
                "processing_state": "uploaded",
                "file_path": "nb_a1b2c3d4/document.pdf",
            }
        }


class PDFListItem(BaseModel):
    """Individual PDF item in list response."""

    filename: str = Field(..., example="document.pdf")
    file_path: str = Field(..., example="nb_a1b2c3d4/document.pdf")
    processing_status: str = Field(
        ...,
        example="complete",
        description="Current processing state of the PDF",
    )
    uploaded_at: datetime = Field(..., description="When the PDF was uploaded")
    pdf_id: int = Field(..., example=1)
    summary: Optional[str] = Field(None, example="This document discusses...")


class PDFListResponse(BaseModel):
    """Response model for listing PDFs in a notebook."""

    notebook: str = Field(..., example="My Notebook", description="Notebook name")
    notebook_id: str = Field(
        ..., example="nb_a1b2c3d4", description="Notebook identifier"
    )
    pdfs: List[PDFListItem] = Field(..., description="List of PDFs in the notebook")


class PDFDeleteResponse(BaseModel):
    """Response model for PDF deletion."""

    message: str = Field(..., example="File 'nb_a1b2c3d4/document.pdf' deleted.")
    file_deleted: bool = Field(
        ..., example=True, description="Whether file was deleted from disk"
    )
    embeddings_deleted: bool = Field(
        ..., example=True, description="Whether embeddings were deleted from Qdrant"
    )
    summary_deleted: bool = Field(
        ..., example=True, description="Whether summary was deleted from database"
    )
    overall_summaries_deleted: int = Field(
        ..., example=0, description="Number of overall summaries deleted"
    )
    pdf_record_deleted: bool = Field(
        ..., example=True, description="Whether PDF record was deleted from database"
    )


class PDFSummaryResponse(BaseModel):
    """Response model for PDF summary endpoint."""

    summary: str = Field(
        ...,
        example="This document discusses the implementation of RAG systems...",
        description="AI-generated summary of the PDF",
    )
    filename: str = Field(..., example="document.pdf")
    notebook: str = Field(..., example="My Notebook")
    notebook_id: str = Field(..., example="nb_a1b2c3d4")


class ErrorResponse(BaseModel):
    """Standard error response model."""

    detail: str = Field(
        ..., example="Notebook 'My Notebook' not found. Create it first."
    )


class HTTPValidationError(BaseModel):
    """Validation error response model."""

    detail: List[dict] = Field(
        ...,
        example=[
            {
                "loc": ["body", "notebook_name"],
                "msg": "field required",
                "type": "value_error.missing",
            }
        ],
    )
