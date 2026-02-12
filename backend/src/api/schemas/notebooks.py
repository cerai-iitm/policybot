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


class ErrorResponse(BaseModel):
    """Error response model."""

    detail: str = Field(
        ..., example="Notebook with title 'My Notebook' already exists."
    )
