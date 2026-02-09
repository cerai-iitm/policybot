"""Notebooks router with comprehensive Swagger documentation."""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from src.schema.db import get_db
from src.schema.notebooks_crud import (
    create_notebook,
    get_notebook_by_title,
    list_notebooks,
)

router = APIRouter(
    prefix="/notebooks",
    tags=["Notebooks"],
)


class NotebookCreateResponse(BaseModel):
    """Response model for notebook creation."""

    id: int = Field(..., example=1, description="Database ID")
    notebook_id: str = Field(
        ..., example="nb_a1b2c3d4", description="Unique identifier"
    )
    title: str = Field(..., example="My Notebook")
    description: str = Field(..., example="Collection of policy documents")
    created_at: str = Field(..., example="2026-02-09T18:34:56")


class NotebookListItem(BaseModel):
    """Individual notebook in list."""

    id: int = Field(..., example=1)
    notebook_id: str = Field(..., example="nb_a1b2c3d4")
    title: str = Field(..., example="My Notebook")
    description: str = Field(..., example="Collection of policy documents")
    created_at: str = Field(..., example="2026-02-09T18:34:56")


class NotebookListResponse(BaseModel):
    """Response model for listing notebooks."""

    notebooks: List[NotebookListItem]


class ErrorResponse(BaseModel):
    """Error response model."""

    detail: str = Field(
        ..., example="Notebook with title 'My Notebook' already exists."
    )


@router.post(
    "/create",
    response_model=NotebookCreateResponse,
    status_code=201,
    summary="Create new notebook",
    description="""Create a new notebook to organize PDF documents.

**Notebook ID:** Auto-generated unique identifier (e.g., `nb_a1b2c3d4`)

**Usage:**
1. Create notebook with title and optional description
2. Upload PDFs to this notebook
3. Process and query PDFs within the notebook context

**Constraints:**
- Notebook titles must be unique
- Notebook IDs are auto-generated and cannot be customized
""",
    responses={
        201: {
            "description": "Notebook created successfully",
            "model": NotebookCreateResponse,
        },
        409: {
            "description": "Notebook with this title already exists",
            "model": ErrorResponse,
        },
    },
)
async def create_new_notebook(
    title: str = Query(
        ...,
        description="Title of the notebook (must be unique)",
        example="My Notebook",
        min_length=1,
        max_length=255,
    ),
    description: str = Query(
        None,
        description="Optional description of the notebook",
        example="Collection of policy documents for review",
        max_length=1000,
    ),
    db: AsyncSession = Depends(get_db),
):
    """Create a new notebook."""
    # Check if notebook with this title already exists
    existing = await get_notebook_by_title(db, title)
    if existing:
        raise HTTPException(
            status_code=409, detail=f"Notebook with title '{title}' already exists."
        )

    notebook = await create_notebook(db, title=title, description=description)

    return JSONResponse(
        status_code=201,
        content={
            "id": notebook.id,
            "notebook_id": notebook.notebook_id,
            "title": notebook.title,
            "description": notebook.description,
            "created_at": notebook.created_at.isoformat(),
        },
    )


@router.get(
    "/list",
    response_model=NotebookListResponse,
    summary="List all notebooks",
    description="Get a list of all notebooks with their metadata.",
    responses={
        200: {
            "description": "List of notebooks returned",
            "model": NotebookListResponse,
        },
    },
)
async def get_notebooks(db: AsyncSession = Depends(get_db)):
    """List all notebooks."""
    notebooks = await list_notebooks(db)

    return {
        "notebooks": [
            {
                "id": nb.id,
                "notebook_id": nb.notebook_id,
                "title": nb.title,
                "description": nb.description,
                "created_at": nb.created_at.isoformat(),
            }
            for nb in notebooks
        ]
    }
