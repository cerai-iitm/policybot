from typing import List, Optional

from pydantic import BaseModel, Field


class NotebookCreateResponse(BaseModel):
    """Response model for notebook creation."""

    id: int = Field(..., example=1, description="Database ID")
    notebook_id: str = Field(
        ..., example="nb_a1b2c3d4", description="Unique identifier"
    )
    title: str = Field(..., example="My Notebook")
    description: Optional[str] = Field(None, example="Collection of policy documents")
    created_at: str = Field(..., example="2026-02-09T18:34:56")


class NotebookListItem(BaseModel):
    """Individual notebook in list."""

    id: int = Field(..., example=1)
    notebook_id: str = Field(..., example="nb_a1b2c3d4")
    title: str = Field(..., example="My Notebook")
    description: Optional[str] = Field(None, example="Collection of policy documents")
    created_at: str = Field(..., example="2026-02-09T18:34:56")


class NotebookListResponse(BaseModel):
    """Response model for listing notebooks."""

    notebooks: List[NotebookListItem]

    # Optional: include PDFs (with contents) for the first notebook in the list
    first_notebook_id: Optional[str] = Field(
        None, example="nb_a1b2c3d4", description="Notebook ID for the first notebook"
    )

    class FirstNotebookPDFItem(BaseModel):
        filename: str = Field(..., example="document.pdf")
        file_path: str = Field(..., example="nb_a1b2c3d4/document.pdf")
        processing_status: str = Field(..., example="complete")
        uploaded_at: str = Field(..., example="2026-02-09T18:34:56")
        pdf_id: int = Field(..., example=1)
        # Base64 encoded PDF contents (may be None if file not available)
        content_base64: Optional[str] = Field(
            None,
            description="Base64 encoded PDF contents for fast initial load",
        )

    first_notebook_pdfs: Optional[List[FirstNotebookPDFItem]] = Field(
        None, description="PDF list (with contents) for the first notebook"
    )


class ErrorResponse(BaseModel):
    """Error response model."""

    detail: str = Field(
        ..., example="Notebook with title 'My Notebook' already exists."
    )
