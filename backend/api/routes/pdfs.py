# api/routes/pdfs.py
import uuid
from pathlib import Path

import aiofiles
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
)
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_user
from api.schemas.pdf import (
    PDFDeleteResponse,
    PDFListResponse,
    PDFResponse,
    PDFUploadResponse,
)
from app.config import get_config
from db.models.notebook import Notebook
from db.models.pdf import PDF
from db.models.user import User
from db.session import AsyncSessionLocal, get_db
from services.pdf_processor import PDFProcessor

router = APIRouter(prefix="/pdfs", tags=["PDFs"])
config = get_config()


def get_upload_path(user_id: int, notebook_id: int) -> Path:
    base = Path(config.upload_dir)
    return base / str(user_id) / str(notebook_id)


async def process_pdf_background(pdf_id: int):
    async with AsyncSessionLocal() as db:
        processor = PDFProcessor()
        try:
            async for _ in processor.process_pdf(pdf_id, db):
                pass
        except Exception:
            pass


@router.post("/", response_model=PDFUploadResponse, status_code=201)
async def upload_pdf(
    background_tasks: BackgroundTasks,
    notebook_id: int = Form(...),
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")

    result = await db.execute(
        select(Notebook).where(Notebook.id == notebook_id, Notebook.user_id == user.id)
    )
    notebook = result.scalar_one_or_none()
    if not notebook:
        raise HTTPException(status_code=404, detail="Notebook not found")

    stored_filename = str(uuid.uuid4()) + ".pdf"
    upload_path = get_upload_path(user.id, notebook_id)
    upload_path.mkdir(parents=True, exist_ok=True)
    file_path = upload_path / stored_filename

    async with aiofiles.open(file_path, "wb") as f:
        content = await file.read()
        await f.write(content)

    relative_path = f"{user.id}/{notebook_id}/{stored_filename}"

    pdf = PDF(
        user_id=user.id,
        notebook_id=notebook_id,
        original_filename=file.filename,
        stored_filename=stored_filename,
        file_path=relative_path,
        processing_status="uploaded",
    )
    db.add(pdf)
    await db.commit()
    await db.refresh(pdf)

    background_tasks.add_task(process_pdf_background, pdf.id)

    return PDFUploadResponse(
        pdf_id=pdf.id,
        original_filename=pdf.original_filename,
        stored_filename=pdf.stored_filename,
        notebook_id=pdf.notebook_id,
        file_path=pdf.file_path,
        processing_status=pdf.processing_status,
        uploaded_at=pdf.uploaded_at,
    )


@router.get("/", response_model=PDFListResponse)
async def list_pdfs(
    notebook_id: int = Query(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Notebook).where(Notebook.id == notebook_id, Notebook.user_id == user.id)
    )
    notebook = result.scalar_one_or_none()
    if not notebook:
        raise HTTPException(status_code=404, detail="Notebook not found")

    result = await db.execute(select(PDF).where(PDF.notebook_id == notebook_id))
    pdfs = result.scalars().all()

    return PDFListResponse(
        notebook_id=str(notebook.notebook_id),
        pdfs=[
            PDFResponse(
                id=pdf.id,
                original_filename=pdf.original_filename,
                stored_filename=pdf.stored_filename,
                notebook_id=pdf.notebook_id,
                processing_status=pdf.processing_status,
                uploaded_at=pdf.uploaded_at,
                summary=pdf.summary,
            )
            for pdf in pdfs
        ],
    )


@router.get("/{pdf_id}", response_model=PDFResponse)
async def get_pdf(
    pdf_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PDF).where(PDF.id == pdf_id, PDF.user_id == user.id)
    )
    pdf = result.scalar_one_or_none()
    if not pdf:
        raise HTTPException(status_code=404, detail="PDF not found")

    return PDFResponse(
        id=pdf.id,
        original_filename=pdf.original_filename,
        stored_filename=pdf.stored_filename,
        notebook_id=pdf.notebook_id,
        processing_status=pdf.processing_status,
        uploaded_at=pdf.uploaded_at,
        summary=pdf.summary,
    )


@router.get("/{pdf_id}/view")
async def view_pdf(
    pdf_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PDF).where(PDF.id == pdf_id, PDF.user_id == user.id)
    )
    pdf = result.scalar_one_or_none()
    if not pdf:
        raise HTTPException(status_code=404, detail="PDF not found")

    full_path = Path(config.upload_dir) / pdf.file_path
    if not full_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")

    return FileResponse(
        str(full_path),
        media_type="application/pdf",
        filename=pdf.original_filename,
    )


@router.delete("/{pdf_id}", response_model=PDFDeleteResponse)
async def delete_pdf(
    pdf_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PDF).where(PDF.id == pdf_id, PDF.user_id == user.id)
    )
    pdf = result.scalar_one_or_none()
    if not pdf:
        raise HTTPException(status_code=404, detail="PDF not found")

    full_path = Path(config.upload_dir) / pdf.file_path
    file_deleted = False
    if full_path.exists():
        try:
            full_path.unlink()
            file_deleted = True
        except Exception:
            pass

    pdf_id = pdf.id

    await db.delete(pdf)
    await db.commit()

    processor = PDFProcessor()
    await processor.delete_embeddings(pdf_id)

    return PDFDeleteResponse(
        message=f"PDF {pdf_id} deleted",
        file_deleted=file_deleted,
        pdf_record_deleted=True,
    )
