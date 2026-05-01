# api/routes/pdfs.py
import asyncio
import logging
import uuid
from pathlib import Path
from typing import Union

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
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from api.deps import get_current_user
from api.schemas.pdf import (
    PDFDeleteResponse,
    PDFListResponse,
    PDFResponse,
    PDFUploadResponse,
    SuggestedQueryResponse,
    FilenameUpdateRequest,
    FilenameUpdateResponse,
)
from app.config import get_config
from db.models.notebook import Notebook
from db.models.pdf import PDF
from db.models.user import User
from db.session import AsyncSessionLocal, get_db
from services.pdf_processor import PDFProcessor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pdfs", tags=["PDFs"])
config = get_config()

_MAX_CONCURRENT = getattr(config, "max_concurrent_processing", 2)
_PROCESS_SEMAPHORE = asyncio.Semaphore(_MAX_CONCURRENT)


async def process_pdf_background(pdf_id: int):
    """Background processing for PDF RAG pipeline."""
    async with AsyncSessionLocal() as bg_db:
        processor = PDFProcessor()
        try:
            async for update in processor.process_pdf(pdf_id, bg_db):
                logger.info(f"[bg:{pdf_id}] {update}")
                if isinstance(update, str) and update.startswith("Error:"):
                    logger.exception(
                        f"[bg:{pdf_id}] Error detected, stopping processing"
                    )
                    break
        except Exception as e:
            logger.exception(f"Background processing failed for pdf_id {pdf_id}")


def get_upload_path(user_id: int, notebook_id: int) -> Path:
    base = Path(config.upload_dir)
    return base / str(user_id) / str(notebook_id)


@router.post("/", response_model=PDFUploadResponse, status_code=201)
async def upload_pdf(
    background_tasks: BackgroundTasks,
    # External API accepts the public notebook_id string
    notebook_id: str = Form(...),
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")

    # Resolve the Notebook by the external notebook_id (string)
    result = await db.execute(
        select(Notebook).where(
            Notebook.notebook_id == notebook_id, Notebook.user_id == user.id
        )
    )
    notebook = result.scalar_one_or_none()
    if not notebook:
        raise HTTPException(status_code=404, detail="Notebook not found")

    # Reuse existing PDF if same notebook + original filename + user
    existing_stmt = select(PDF).where(
        PDF.notebook_id == notebook.id,
        PDF.original_filename == file.filename,
        PDF.user_id == user.id,
    )
    existing_res = await db.execute(existing_stmt)
    existing_pdf = existing_res.scalar_one_or_none()

    if existing_pdf:
        # If it's already complete, just return it; otherwise re-enqueue processing
        if existing_pdf.processing_status == "complete":
            return PDFUploadResponse(
                stored_filename=existing_pdf.stored_filename,
                original_filename=existing_pdf.original_filename,
                notebook_id=str(notebook.notebook_id),
                file_path=existing_pdf.file_path,
                processing_status=existing_pdf.processing_status,
                uploaded_at=existing_pdf.uploaded_at,
            )

        # Reuse row for in-progress PDF: do not overwrite file on disk.
        background_tasks.add_task(process_pdf_background, existing_pdf.id)
        return PDFUploadResponse(
            stored_filename=existing_pdf.stored_filename,
            original_filename=existing_pdf.original_filename,
            notebook_id=str(notebook.notebook_id),
            file_path=existing_pdf.file_path,
            processing_status=existing_pdf.processing_status,
            uploaded_at=existing_pdf.uploaded_at,
        )

    # No existing PDF: create new record and save file
    stored_filename = str(uuid.uuid4())
    upload_path = get_upload_path(user.id, notebook.id)
    upload_path.mkdir(parents=True, exist_ok=True)
    file_path = upload_path / f"{stored_filename}.pdf"

    async with aiofiles.open(file_path, "wb") as f:
        content = await file.read()
        await f.write(content)

    relative_path = f"{user.id}/{notebook.id}/{stored_filename}.pdf"

    pdf = PDF(
        user_id=user.id,
        notebook_id=notebook.id,
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
        stored_filename=pdf.stored_filename,
        original_filename=pdf.original_filename,
        notebook_id=str(notebook.notebook_id),
        file_path=pdf.file_path,
        processing_status=pdf.processing_status,
        uploaded_at=pdf.uploaded_at,
    )


@router.get("/", response_model=Union[PDFResponse, PDFListResponse])
async def get_pdfs(
    pdf_id: str = Query(None, description="PDF stored_filename to retrieve single PDF"),
    notebook_id: str = Query(None, description="Notebook ID to list all PDFs"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get PDF(s) by either:
    - pdf_id: returns single PDF with suggested queries
    - notebook_id: returns list of all PDFs in notebook
    """
    if not pdf_id and not notebook_id:
        raise HTTPException(
            status_code=400,
            detail="Provide either pdf_id or notebook_id query parameter",
        )

    if pdf_id:
        # Return single PDF by stored_filename
        result = await db.execute(
            select(PDF)
            .options(selectinload(PDF.suggested_queries))
            .where(PDF.stored_filename == pdf_id, PDF.user_id == user.id)
        )
        pdf = result.scalar_one_or_none()
        if not pdf:
            raise HTTPException(status_code=404, detail="PDF not found")

        # lookup notebook to get external notebook_id string
        notebook = await db.get(Notebook, pdf.notebook_id)
        notebook_id_str = str(notebook.notebook_id) if notebook else ""

        return PDFResponse(
            stored_filename=pdf.stored_filename,
            original_filename=pdf.original_filename,
            notebook_id=notebook_id_str,
            processing_status=pdf.processing_status,
            uploaded_at=pdf.uploaded_at,
            summary=pdf.summary,
            suggested_queries=[
                SuggestedQueryResponse(
                    query_text=sq.query_text,
                    order_index=sq.order_index,
                )
                for sq in (pdf.suggested_queries or [])
            ],
        )

    if notebook_id:
        # Return list of PDFs in notebook
        result = await db.execute(
            select(Notebook).where(
                Notebook.notebook_id == notebook_id, Notebook.user_id == user.id
            )
        )
        notebook = result.scalar_one_or_none()
        if not notebook:
            raise HTTPException(status_code=404, detail="Notebook not found")

        # Use numeric notebook.id for querying PDF FK
        result = await db.execute(select(PDF).where(PDF.notebook_id == notebook.id))
        pdfs = result.scalars().all()

        return PDFListResponse(
            notebook_id=str(notebook.notebook_id),
            pdfs=[
                PDFResponse(
                    stored_filename=pdf.stored_filename,
                    original_filename=pdf.original_filename,
                    notebook_id=str(notebook.notebook_id),
                    processing_status=pdf.processing_status,
                    uploaded_at=pdf.uploaded_at,
                    summary=pdf.summary,
                )
                for pdf in pdfs
            ],
        )


@router.get("/view")
async def view_pdf(
    pdf_id: str = Query(..., description="PDF stored_filename"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """View/Download PDF file by stored_filename."""
    result = await db.execute(
        select(PDF).where(PDF.stored_filename == pdf_id, PDF.user_id == user.id)
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


@router.delete("/", response_model=PDFDeleteResponse)
async def delete_pdf(
    pdf_id: str = Query(..., description="PDF stored_filename to delete"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete PDF by stored_filename."""
    result = await db.execute(
        select(PDF).where(PDF.stored_filename == pdf_id, PDF.user_id == user.id)
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

    stored_filename = pdf.stored_filename

    await db.delete(pdf)
    await db.commit()

    processor = PDFProcessor()
    await processor.delete_embeddings(stored_filename)

    return PDFDeleteResponse(
        message=f"PDF {stored_filename} deleted",
        file_deleted=file_deleted,
        pdf_record_deleted=True,
    )


@router.patch("/filename", response_model=FilenameUpdateResponse)
async def update_pdf_filename(
    pdf_id: str = Query(..., description="PDF stored_filename"),
    request: FilenameUpdateRequest = ...,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update PDF's original_filename by stored_filename."""
    result = await db.execute(
        select(PDF).where(PDF.stored_filename == pdf_id, PDF.user_id == user.id)
    )
    pdf = result.scalar_one_or_none()
    if not pdf:
        raise HTTPException(status_code=404, detail="PDF not found")

    pdf.original_filename = request.original_filename
    await db.commit()
    await db.refresh(pdf)

    notebook = await db.get(Notebook, pdf.notebook_id)
    notebook_id_str = str(notebook.notebook_id) if notebook else ""

    return FilenameUpdateResponse(
        stored_filename=pdf.stored_filename,
        original_filename=pdf.original_filename,
        notebook_id=notebook_id_str,
    )


@router.get("/process")
async def pdf_process_sse(
    notebook_id: str = Query(...),
    pdf_id: str = Query(..., description="PDF stored_filename"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    SSE endpoint to stream PDF processing status.

    Query params:
    - notebook_id: external notebook id string (e.g. nb_xxx)
    - pdf_id: the PDF's stored_filename string identifier

    Yields plain SSE events:
    data: uploaded
    data: embeddings_complete
    data: complete
    data: done
    """
    # Resolve notebook by external string identifier
    res = await db.execute(
        select(Notebook).where(
            Notebook.notebook_id == notebook_id, Notebook.user_id == user.id
        )
    )
    notebook = res.scalar_one_or_none()
    if not notebook:
        raise HTTPException(status_code=404, detail="Notebook not found")

    # Resolve PDF by stored_filename (pdf_id param) and notebook
    res = await db.execute(
        select(PDF).where(
            PDF.stored_filename == pdf_id,
            PDF.notebook_id == notebook.id,
            PDF.user_id == user.id,
        )
    )
    pdf = res.scalar_one_or_none()
    if not pdf:
        raise HTTPException(status_code=404, detail="PDF not found")

    pdf_internal_id = pdf.id

    async def generate():
        start_time = asyncio.get_event_loop().time()
        max_duration = 15 * 60  # 15 minutes
        try:
            while True:
                elapsed = asyncio.get_event_loop().time() - start_time
                if elapsed > max_duration:
                    logger.warning(f"Processing timeout for pdf_id={pdf_id}")
                    yield "data: error\n\n"
                    yield "data: done\n\n"
                    break

                # Refresh PDF status from DB
                try:
                    await db.refresh(pdf)
                except Exception:
                    # If refresh fails, re-fetch
                    r = await db.execute(
                        select(PDF).where(
                            PDF.id == pdf_internal_id, PDF.user_id == user.id
                        )
                    )
                    pdf_local = r.scalar_one_or_none()
                    if pdf_local:
                        pdf = pdf_local

                status = pdf.processing_status or "uploaded"
                yield f"data: {status}\n\n"

                if status in ["complete", "error"]:
                    yield "data: done\n\n"
                    break

                await asyncio.sleep(2)

        except asyncio.CancelledError:
            logger.info(f"SSE connection closed for pdf_id={pdf_id}")
        except Exception as e:
            logger.exception(f"Error in SSE stream for pdf_id={pdf_id}")
            yield "data: error\n\n"
            yield "data: done\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
