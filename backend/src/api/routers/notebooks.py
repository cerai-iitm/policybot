"""Notebooks router with comprehensive Swagger documentation."""

import asyncio
from fastapi import APIRouter, Depends, Form
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas import (
    NotebookCreateResponse,
    NotebookListResponse,
)
from src.core import cfg
from src.db import get_db
from src.db.crud import get_pdfs_by_notebook
from src.services.notebooks import create_notebook as svc_create_notebook
from src.services.notebooks import list_notebooks as svc_list_notebooks

router = APIRouter(
    prefix="/notebooks",
    tags=["Notebooks"],
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
)
async def create_new_notebook(
    title: str = Form(
        ...,
        description="Title of the notebook (must be unique)",
        example="My Notebook",
        min_length=1,
        max_length=255,
    ),
    description: str = Form(
        None,
        description="Optional description of the notebook",
        example="Collection of policy documents for review",
        max_length=1000,
    ),
    db: AsyncSession = Depends(get_db),
):
    """Create a new notebook."""
    return await svc_create_notebook(db, title=title, description=description)


@router.get(
    "/list",
    response_model=NotebookListResponse,
    summary="List all notebooks",
    description="Get a list of all notebooks with their metadata.",
)
async def get_notebooks(db: AsyncSession = Depends(get_db)):
    """List all notebooks."""
    nbs = await svc_list_notebooks(db)

    first_notebook_id = None
    first_notebook_pdfs = None

    if nbs:
        first_notebook = nbs[0]
        first_notebook_id = first_notebook["notebook_id"]

        pdfs = await get_pdfs_by_notebook(db, first_notebook["id"])

        first_notebook_pdfs = []
        for pdf in pdfs:
            if pdf.processing_status == "complete":
                first_notebook_pdfs.append(
                    {
                        "filename": pdf.file_name,
                        "file_path": pdf.file_path,
                        "processing_status": pdf.processing_status,
                        "uploaded_at": pdf.uploaded_at.isoformat(),
                        "pdf_id": pdf.id,
                    }
                )

    return {
        "notebooks": nbs,
        "first_notebook_id": first_notebook_id,
        "first_notebook_pdfs": first_notebook_pdfs,
    }
