# api/routes/notebooks.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import secrets

from api.deps import get_current_user
from db.session import get_db
from db.models import User, Notebook, PDF
from sqlalchemy.orm import selectinload
from api.schemas.notebook import (
    NotebookCreate,
    NotebookResponse,
    NotebookListResponse,
    NotebookUpdate,
    PDFDetailsRequest,
    PDFDetailsResponse,
    PDFDetailItem,
)

router = APIRouter(prefix="/notebooks", tags=["notebooks"])


@router.post("", response_model=NotebookResponse, status_code=status.HTTP_201_CREATED)
async def create_notebook(
    notebook_data: NotebookCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    notebook = Notebook(
        notebook_id=f"nb_{secrets.token_hex(8)}",
        user_id=current_user.id,
        title=notebook_data.title,
        description=notebook_data.description,
    )
    db.add(notebook)
    await db.commit()
    await db.refresh(notebook)
    return notebook


@router.get("", response_model=NotebookListResponse)
async def list_notebooks(
    notebook_id: str | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(Notebook)
        .options(selectinload(Notebook.pdfs))
        .where(Notebook.user_id == current_user.id)
    )
    if notebook_id:
        query = query.where(Notebook.notebook_id == notebook_id)
    result = await db.execute(query)
    notebooks = result.scalars().all()

    notebooks_with_count = [
        {
            "id": nb.id,
            "notebook_id": nb.notebook_id,
            "title": nb.title,
            "description": nb.description,
            "created_at": nb.created_at,
            "processed_pdf_count": sum(
                1 for pdf in nb.pdfs if pdf.processing_status == "complete"
            ),
        }
        for nb in notebooks
    ]
    return {"notebooks": notebooks_with_count}


@router.get("/{notebook_id}", response_model=NotebookResponse)
async def get_notebook(
    notebook_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Notebook).where(
            Notebook.notebook_id == notebook_id, Notebook.user_id == current_user.id
        )
    )
    notebook = result.scalar_one_or_none()
    if not notebook:
        raise HTTPException(status_code=404, detail="Notebook not found")
    return notebook


@router.delete("/{notebook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notebook(
    notebook_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Notebook).where(
            Notebook.notebook_id == notebook_id, Notebook.user_id == current_user.id
        )
    )
    notebook = result.scalar_one_or_none()
    if not notebook:
        raise HTTPException(status_code=404, detail="Notebook not found")
    await db.delete(notebook)
    await db.commit()


@router.post("/update", response_model=NotebookResponse)
async def update_notebook(
    notebook_id: str,
    notebook_data: NotebookUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Notebook).where(
            Notebook.notebook_id == notebook_id, Notebook.user_id == current_user.id
        )
    )
    notebook = result.scalar_one_or_none()
    if not notebook:
        raise HTTPException(status_code=404, detail="Notebook not found")

    if notebook_data.title is not None:
        notebook.title = notebook_data.title
    if notebook_data.description is not None:
        notebook.description = notebook_data.description

    await db.commit()
    await db.refresh(notebook)
    return notebook


@router.post("/pdf-details", response_model=PDFDetailsResponse)
async def get_pdf_details(
    request: PDFDetailsRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Notebook).where(
            Notebook.notebook_id == request.notebook_id,
            Notebook.user_id == current_user.id,
        )
    )
    notebook = result.scalar_one_or_none()
    if not notebook:
        raise HTTPException(status_code=404, detail="Notebook not found")

    query = (
        select(PDF)
        .options(selectinload(PDF.suggested_queries))
        .where(PDF.notebook_id == notebook.id, PDF.user_id == current_user.id)
    )

    if request.pdf_ids:
        query = query.where(PDF.stored_filename.in_(request.pdf_ids))

    result = await db.execute(query)
    pdfs = result.scalars().all()

    return PDFDetailsResponse(
        pdfs=[
            PDFDetailItem(
                pdf_id=pdf.stored_filename,
                filename=pdf.original_filename,
                summary=pdf.summary,
                suggested_queries=[
                    sq.query_text for sq in (pdf.suggested_queries or [])
                ],
            )
            for pdf in pdfs
        ]
    )
