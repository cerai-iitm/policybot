import asyncio
import os
from pathlib import Path

import aiofiles
from fastapi import (
    APIRouter,
    BackgroundTasks,  # Added for background processing
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
)
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.core import cfg, logger
from src.db import get_db
from src.db.config import AsyncSessionLocal
from src.db.crud import (
    create_pdf,
    delete_overall_summaries_containing_file,
    delete_source_summary,
    get_notebook_by_notebook_id,
    get_pdf_by_filename_and_notebook,
    get_pdfs_by_notebook,
    get_summary_by_source_name,
)
from src.db.crud import (
    delete_pdf as delete_pdf_record,
)
from src.db.schema import PDF
from src.services import PDFProcessor

from ..schemas import (
    ErrorResponse,
    PDFDeleteResponse,
    PDFListResponse,
    PDFSummaryResponse,
    PDFUploadResponse,
)

router = APIRouter(
    tags=["PDF Processing"],
    responses={
        500: {
            "description": "Internal server error",
            "model": ErrorResponse,
        },
    },
)

# limit concurrent background processing to avoid resource exhaustion
_MAX_CONCURRENT = getattr(cfg, "MAX_CONCURRENT_PROCESSING", 2)
_PROCESS_SEMAPHORE = asyncio.Semaphore(_MAX_CONCURRENT)


async def _get_processing_state_from_db(
    file_name: str, notebook_id: int, db: AsyncSession
) -> tuple[str, PDF | None]:
    """Check processing state from database (fast single query)."""
    logger.info(
        f"Checking DB processing state for file: {file_name} in notebook: {notebook_id}"
    )

    pdf = await get_pdf_by_filename_and_notebook(db, file_name, notebook_id)

    if not pdf:
        logger.info(f"File {file_name} not found in notebook {notebook_id} - new file")
        return "new", None

    logger.info(f"Found PDF record with status: {pdf.processing_status}")
    return pdf.processing_status, pdf


async def process_pdf_background(file_name: str, pdf_id: int):
    """Background processing for PDF RAG pipeline."""
    async with AsyncSessionLocal() as bg_db:
        pdf_processor = PDFProcessor()
        try:
            async for update in pdf_processor.process_pdf(
                file_name, pdf_id=pdf_id, db=bg_db
            ):
                logger.info(f"[bg:{pdf_id}] {update}")
        except Exception as e:
            logger.error(f"Background processing failed for {file_name}: {e}")
            await update_pdf_status(bg_db, pdf_id, "error")


@router.post(
    "/upload",
    response_model=PDFUploadResponse,
    status_code=201,
    summary="Upload PDF to notebook",
    description="""Upload a PDF file to a specific notebook with background processing.

**Processing States:**
- `uploaded`: File uploaded, processing starting
- `processing`: Text extraction and chunking
- `embeddings_complete`: Embeddings stored, summary pending
- `summary_generation`: Summary being generated
- `complete`: Fully processed

**Notes:**
- Only PDF files accepted
- File names must be unique within notebook
- Duplicate uploads return current state
- Background processing starts immediately after upload
""",
    responses={
        201: {"description": "PDF uploaded successfully", "model": PDFUploadResponse},
        200: {
            "description": "PDF already exists, returned current state",
            "model": PDFUploadResponse,
        },
        400: {"description": "Invalid input", "model": ErrorResponse},
        404: {"description": "Notebook not found", "model": ErrorResponse},
        409: {"description": "PDF already fully processed", "model": ErrorResponse},
    },
)
async def upload_pdf(
    background_tasks: BackgroundTasks,
    notebook_id: str = Form(
        ..., description="Notebook ID (e.g., nb_abc123)", example="nb_a1b2c3d4"
    ),
    file: UploadFile = File(..., description="PDF file", media_type="application/pdf"),
    db: AsyncSession = Depends(get_db),
):
    """Upload a PDF file to a notebook with background RAG processing."""
    logger.info(f"Upload request - notebook_id: {notebook_id}, file: {file.filename}")

    # Validate inputs
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded.")
    if not notebook_id.strip():
        raise HTTPException(status_code=400, detail="Notebook ID is required.")
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400, detail="Invalid file format. Please upload a PDF."
        )

    # Check notebook exists
    notebook = await get_notebook_by_notebook_id(db, notebook_id.strip())
    if not notebook:
        raise HTTPException(
            status_code=404, detail=f"Notebook '{notebook_id}' not found."
        )

    # Check processing state
    processing_state, existing_pdf = await _get_processing_state_from_db(
        file.filename, notebook.id, db
    )
    if processing_state == "complete":
        return JSONResponse(
            status_code=409,
            content={
                "detail": "File already exists and is fully processed.",
                "filename": file.filename,
                "notebook": notebook.title,
                "notebook_id": notebook.notebook_id,
                "processing_state": "complete",
            },
        )

    if existing_pdf and processing_state == "error":
        return JSONResponse(
            status_code=500,
            content={
                "detail": "PDF is in error state. Please investigate.",
                "filename": file.filename,
                "notebook": notebook.title,
                "notebook_id": notebook.notebook_id,
                "processing_state": "error",
            },
        )

    if existing_pdf:
        background_tasks.add_task(
            process_pdf_background, file.filename, existing_pdf.id
        )
        return JSONResponse(
            status_code=200,
            content={
                "message": "Background processing resumed for existing PDF.",
                "filename": file.filename,
                "notebook": notebook.title,
                "notebook_id": notebook.notebook_id,
                "processing_state": processing_state,
            },
        )

    # New upload: save file
    import os

    upload_dir = Path(cfg.DATA_DIR) / notebook.notebook_id
    os.makedirs(upload_dir, exist_ok=True)  # Ensure dir exists
    file_path = upload_dir / file.filename

    async with aiofiles.open(file_path, "wb") as buffer:
        content = await file.read()
        await buffer.write(content)

    # Create DB record
    relative_path = f"{notebook.notebook_id}/{file.filename}"
    pdf = await create_pdf(
        db=db, file_name=file.filename, file_path=relative_path, notebook_id=notebook.id
    )

    # Start background processing
    background_tasks.add_task(process_pdf_background, file.filename, pdf.id)

    return JSONResponse(
        status_code=201,
        content={
            "filename": file.filename,
            "notebook": notebook.title,
            "notebook_id": notebook.notebook_id,
            "pdf_id": pdf.id,
            "processing_state": "uploaded",
            "file_path": relative_path,
        },
    )


@router.get(
    "/list",
    response_model=PDFListResponse,
    summary="List PDFs in notebook",
    description="Get all PDFs in a specific notebook with their current processing status.",
    responses={
        200: {
            "description": "List of PDFs returned successfully",
            "model": PDFListResponse,
        },
        404: {
            "description": "Notebook not found",
            "model": ErrorResponse,
        },
    },
)
async def list_pdfs(
    notebook_id: str = Query(
        ...,
        description="Notebook ID (e.g., nb_abc123)",
        example="nb_a1b2c3d4",
    ),
    db: AsyncSession = Depends(get_db),
):
    """List all PDFs in a notebook with current processing status."""
    logger.info(f"List PDFs request for notebook_id: {notebook_id}")

    # Check if notebook exists
    notebook = await get_notebook_by_notebook_id(db, notebook_id.strip())
    if not notebook:
        raise HTTPException(
            status_code=404, detail=f"Notebook '{notebook_id}' not found."
        )

    try:
        # Get PDFs from database
        pdfs = await get_pdfs_by_notebook(db, notebook.id)

        pdf_list = []
        for pdf in pdfs:
            pdf_list.append(
                {
                    "filename": pdf.file_name,
                    "file_path": pdf.file_path,
                    "processing_status": pdf.processing_status,
                    "uploaded_at": pdf.uploaded_at.isoformat(),
                    "pdf_id": pdf.id,
                }
            )

        return JSONResponse(
            content={
                "notebook": notebook.title,
                "notebook_id": notebook.notebook_id,
                "pdfs": pdf_list,
            },
            status_code=200,
        )
    except Exception as e:
        logger.error(f"Failed to list PDFs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list PDFs: {str(e)}")


async def _delete_pdf_file(file_path: Path) -> bool:
    """Helper to delete PDF file from disk."""
    try:
        logger.info(f"Attempting to delete PDF file: {file_path}")
        await asyncio.to_thread(os.remove, str(file_path))
        logger.info(f"Successfully deleted PDF file: {file_path}")
        return True
    except FileNotFoundError:
        logger.warning(f"PDF file not found during deletion: {file_path}")
        return False


async def _perform_deletion(file_path: str, db: AsyncSession) -> tuple[int, dict]:
    """
    Shared deletion logic.
    file_path should be the relative path (e.g., "nb_abc123/file.pdf")
    """
    logger.info(f"Performing deletion for PDF: {file_path}")

    # Parse file_path to get notebook_id and filename
    parts = file_path.split("/")
    if len(parts) != 2:
        raise HTTPException(
            status_code=400,
            detail="Invalid file path. Expected format: {notebook_id}/{filename}",
        )

    notebook_id_str, filename = parts

    if not filename.lower().endswith(".pdf"):
        logger.warning(f"Invalid file format in delete request: {filename}")
        raise HTTPException(
            status_code=400,
            detail="Invalid file format. Please specify a PDF file to delete.",
        )

    # Look up the notebook
    from src.db.crud import get_notebook_by_notebook_id

    notebook = await get_notebook_by_notebook_id(db, notebook_id_str)
    if not notebook:
        raise HTTPException(
            status_code=404, detail=f"Notebook '{notebook_id_str}' not found"
        )

    # Look up the PDF record
    pdf = await get_pdf_by_filename_and_notebook(db, filename, notebook.id)
    if not pdf:
        logger.warning(f"PDF record not found in DB: {file_path}")

    full_path = Path(cfg.DATA_DIR) / file_path
    file_exists = await asyncio.to_thread(full_path.exists)

    if not file_exists and not pdf:
        logger.warning(f"Delete request for non-existent file: {file_path}")
        raise HTTPException(status_code=404, detail="File not found.")

    try:
        logger.info(f"Starting deletion operations for: {file_path}")
        pdf_processor = PDFProcessor()

        # Run non-DB operations in parallel
        file_deleted, embeddings_deleted = await asyncio.gather(
            _delete_pdf_file(full_path) if file_exists else asyncio.sleep(0),
            pdf_processor.delete_embeddings(filename),
            return_exceptions=True,
        )

        # Run DB operations
        summary_result = await delete_source_summary(db, filename)

        try:
            overall_deleted = await delete_overall_summaries_containing_file(
                db, filename
            )
        except Exception as overall_exc:
            try:
                await db.rollback()
            except Exception:
                pass
            overall_deleted = overall_exc

        # Delete PDF record from database
        pdf_record_deleted = False
        if pdf:
            try:
                await delete_pdf_record(db, pdf.id)
                pdf_record_deleted = True
                logger.info(f"Deleted PDF record from database: {file_path}")
            except Exception as pdf_del_err:
                logger.error(f"Failed to delete PDF record: {pdf_del_err}")

        logger.info(f"Deletion operations completed for {file_path}")

        failures = []
        if file_exists and isinstance(file_deleted, Exception):
            logger.error(f"File deletion failed: {file_deleted}")
            failures.append("file")
        elif file_exists and not file_deleted:
            failures.append("file")

        if isinstance(embeddings_deleted, Exception):
            logger.error(f"Embeddings deletion failed: {embeddings_deleted}")
            failures.append("embeddings")

        if isinstance(summary_result, Exception):
            logger.error(f"Summary deletion failed: {summary_result}")
            failures.append("summary")

        if isinstance(overall_deleted, Exception):
            logger.error(f"Overall summary deletion failed: {overall_deleted}")
            failures.append("overall summaries")

        if pdf and not pdf_record_deleted:
            failures.append("pdf_record")

        return 200, {
            "message": f"File '{file_path}' deleted.",
            "file_deleted": (
                bool(file_deleted) and not isinstance(file_deleted, Exception)
            )
            if file_exists
            else True,
            "embeddings_deleted": bool(embeddings_deleted)
            and not isinstance(embeddings_deleted, Exception),
            "summary_deleted": not isinstance(summary_result, Exception)
            and summary_result is not None,
            "overall_summaries_deleted": 0
            if isinstance(overall_deleted, Exception)
            else int(overall_deleted)
            if isinstance(overall_deleted, int)
            else 0,
            "pdf_record_deleted": pdf_record_deleted,
        }
    except Exception as e:
        logger.error(f"Error during deletion: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")


@router.post(
    "/remove",
    response_model=PDFDeleteResponse,
    summary="Delete PDF (POST method)",
    description="""Delete a PDF and all associated data using POST method (firewall-friendly).

**Deletes:**
- PDF file from disk
- Embeddings from Qdrant vector store
- Summary from database
- PDF record from database
- Overall summaries containing this file

**Note:** Notebook ID and filename are sent as form data.
""",
    responses={
        200: {
            "description": "PDF deleted successfully",
            "model": PDFDeleteResponse,
        },
        400: {
            "description": "Invalid or missing form data",
            "model": ErrorResponse,
        },
        404: {
            "description": "Notebook or PDF not found",
            "model": ErrorResponse,
        },
    },
)
async def remove_pdf(
    notebook_id: str = Form(
        ...,
        description="Notebook ID (e.g., nb_abc123)",
        example="nb_a1b2c3d4",
    ),
    filename: str = Form(
        ...,
        description="PDF filename",
        example="document.pdf",
    ),
    db: AsyncSession = Depends(get_db),
):
    """Remove a PDF by notebook ID and filename (POST for firewall compatibility)."""
    logger.info(f"Remove request for notebook_id: {notebook_id}, filename: {filename}")

    # Validate inputs
    if not notebook_id or not notebook_id.strip():
        logger.warning("Remove request rejected - missing or empty notebook_id")
        raise HTTPException(
            status_code=400,
            detail="notebook_id is required and cannot be empty.",
        )
    if not filename or not filename.strip():
        logger.warning("Remove request rejected - missing or empty filename")
        raise HTTPException(
            status_code=400,
            detail="filename is required and cannot be empty.",
        )
    if not filename.lower().endswith(".pdf"):
        logger.warning(f"Remove request rejected - invalid filename: {filename}")
        raise HTTPException(
            status_code=400,
            detail="Invalid filename. Please specify a PDF file.",
        )

    # Construct file_path for _perform_deletion
    file_path = f"{notebook_id.strip()}/{filename.strip()}"
    logger.info(f"Constructed file_path: {file_path}")

    status_code, content = await _perform_deletion(file_path, db)
    return JSONResponse(status_code=status_code, content=content)


@router.get(
    "/process",
    summary="Monitor PDF processing status",
    description="""Monitor the processing status of a PDF in real-time via Server-Sent Events (SSE).

**Returns:** SSE stream with status updates every 2 seconds.

**Status Values:**
- uploaded: File uploaded, processing pending
- processing: Text extraction and chunking
- embeddings_complete: Embeddings stored, summary pending
- summary_generation: Summary being generated
- complete: Fully processed
- error: Processing failed

**Example Events:**
```
data: uploaded

data: processing

data: complete

data: done
```
""",
    responses={
        200: {
            "description": "SSE stream of status updates",
            "content": {
                "text/event-stream": {"example": "data: processing\n\ndata: done\n\n"}
            },
        },
        400: {
            "description": "Invalid or missing query parameters",
            "model": ErrorResponse,
        },
        404: {
            "description": "Notebook or PDF not found",
            "model": ErrorResponse,
        },
    },
)
async def process_status(
    notebook_id: str = Query(
        ...,
        description="Notebook ID (e.g., nb_abc123)",
        example="nb_a1b2c3d4",
    ),
    filename: str = Query(
        ...,
        description="PDF filename",
        example="document.pdf",
    ),
    db: AsyncSession = Depends(get_db),
):
    """Monitor PDF processing status via SSE."""
    logger.info(
        f"Status monitor request for notebook_id: {notebook_id}, filename: {filename}"
    )

    # Validate inputs
    if not notebook_id or not notebook_id.strip():
        logger.warning("Status monitor rejected - missing or empty notebook_id")
        raise HTTPException(
            status_code=400,
            detail="notebook_id is required and cannot be empty.",
        )
    if not filename or not filename.strip():
        logger.warning("Status monitor rejected - missing or empty filename")
        raise HTTPException(
            status_code=400,
            detail="filename is required and cannot be empty.",
        )
    if not filename.lower().endswith(".pdf"):
        logger.warning(f"Status monitor rejected - invalid filename: {filename}")
        raise HTTPException(
            status_code=400,
            detail="Invalid filename. Please specify a PDF file.",
        )

    # Look up the notebook
    notebook = await get_notebook_by_notebook_id(db, notebook_id.strip())
    if not notebook:
        logger.warning(f"Status monitor rejected - notebook not found: {notebook_id}")
        raise HTTPException(
            status_code=404, detail=f"Notebook '{notebook_id}' not found"
        )

    logger.info(f"Found notebook: {notebook.title} (ID: {notebook.id})")

    # Verify PDF exists in notebook
    pdf = await get_pdf_by_filename_and_notebook(db, filename.strip(), notebook.id)
    if not pdf:
        logger.warning(
            f"Status monitor rejected - PDF not found: {filename} in notebook {notebook_id}"
        )
        raise HTTPException(
            status_code=404,
            detail=f"PDF '{filename}' not found in notebook '{notebook_id}'",
        )

    logger.info(
        f"Monitoring PDF: {filename} (ID: {pdf.id}, initial status: {pdf.processing_status})"
    )

    async def generate():
        try:
            while True:
                # Refresh PDF status from DB
                await db.refresh(pdf)
                status = pdf.processing_status
                logger.debug(f"Current status for {filename}: {status}")

                yield f"data: {status}\n\n"

                # Stop if complete or error
                if status in ["complete", "error"]:
                    yield "data: done\n\n"
                    break

                # Poll every 2 seconds
                await asyncio.sleep(2)
        except asyncio.CancelledError:
            logger.info(f"SSE connection closed for {filename}")
        except Exception as e:
            logger.error(f"Error in SSE stream for {filename}: {e}")
            yield "data: error\n\ndata: done\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.get(
    "/view",
    response_class=FileResponse,
    summary="View or download PDF",
    description="""View or download a PDF file directly.
**Returns:** The PDF file with `application/pdf` content type.
**Usage:**
- Browser: Opens PDF viewer or download dialog
- API clients: Receive raw PDF bytes
""",
    responses={
        200: {
            "description": "PDF file",
            "content": {"application/pdf": {}},
        },
        400: {
            "description": "Invalid or missing query parameters",
            "model": ErrorResponse,
        },
        404: {
            "description": "Notebook, PDF, or file not found",
            "model": ErrorResponse,
        },
    },
)
async def view_pdf(
    notebook_id: str = Query(
        ...,
        description="Notebook ID (e.g., nb_abc123)",
        example="nb_a1b2c3d4",
    ),
    filename: str = Query(
        ...,
        description="PDF filename",
        example="document.pdf",
    ),
    db: AsyncSession = Depends(get_db),
):
    """View a PDF file."""
    logger.info(f"View request for notebook_id: {notebook_id}, filename: {filename}")
    # Validate inputs
    if not notebook_id or not notebook_id.strip():
        logger.warning("View request rejected - missing or empty notebook_id")
        raise HTTPException(
            status_code=400,
            detail="notebook_id is required and cannot be empty.",
        )
    if not filename or not filename.strip():
        logger.warning("View request rejected - missing or empty filename")
        raise HTTPException(
            status_code=400,
            detail="filename is required and cannot be empty.",
        )
    if not filename.lower().endswith(".pdf"):
        logger.warning(f"View request rejected - invalid filename: {filename}")
        raise HTTPException(
            status_code=400,
            detail="Invalid filename. Please specify a PDF file.",
        )
    # Look up the notebook
    notebook = await get_notebook_by_notebook_id(db, notebook_id.strip())
    if not notebook:
        logger.warning(f"View request rejected - notebook not found: {notebook_id}")
        raise HTTPException(
            status_code=404, detail=f"Notebook '{notebook_id}' not found"
        )
    logger.info(f"Found notebook: {notebook.title} (ID: {notebook.id})")
    # Verify PDF exists in notebook
    pdf = await get_pdf_by_filename_and_notebook(db, filename.strip(), notebook.id)
    if not pdf:
        logger.warning(
            f"View request rejected - PDF not found: {filename} in notebook {notebook_id}"
        )
        raise HTTPException(
            status_code=404,
            detail=f"PDF '{filename}' not found in notebook '{notebook_id}'",
        )
    logger.info(
        f"Found PDF: {filename} (ID: {pdf.id}, status: {pdf.processing_status})"
    )
    # Build file path and check existence
    full_path = Path(cfg.DATA_DIR) / notebook.notebook_id / filename.strip()
    exists = await asyncio.to_thread(full_path.exists)
    if not exists:
        logger.error(f"File exists in DB but not on disk: {full_path}")
        raise HTTPException(status_code=404, detail="PDF not found on disk")
    logger.info(f"Successfully serving PDF: {filename}")
    return FileResponse(
        str(full_path), media_type="application/pdf", filename=filename.strip()
    )


@router.get(
    "/summary",
    response_model=PDFSummaryResponse,
    summary="Get PDF summary",
    description="""Retrieve the AI-generated summary for a processed PDF.
**Note:** PDF must be in `complete` status to have a summary.
**Summary Generation:**
- Uses map-reduce summarization chain
- Processes all text chunks to create comprehensive summary
- Stored in database for quick retrieval
""",
    responses={
        200: {
            "description": "Summary retrieved successfully",
            "model": PDFSummaryResponse,
        },
        400: {
            "description": "Invalid or missing query parameters",
            "model": ErrorResponse,
        },
        404: {
            "description": "Notebook, PDF, or summary not found",
            "model": ErrorResponse,
        },
    },
)
async def get_summary(
    notebook_id: str = Query(
        ...,
        description="Notebook ID (e.g., nb_abc123)",
        example="nb_a1b2c3d4",
    ),
    filename: str = Query(
        ...,
        description="PDF filename",
        example="document.pdf",
    ),
    db: AsyncSession = Depends(get_db),
):
    """Get the summary for a processed PDF."""
    logger.info(
        f"Fetching summary for notebook_id: {notebook_id}, filename: {filename}"
    )
    # Validate inputs
    if not notebook_id or not notebook_id.strip():
        logger.warning("Summary request rejected - missing or empty notebook_id")
        raise HTTPException(
            status_code=400,
            detail="notebook_id is required and cannot be empty.",
        )
    if not filename or not filename.strip():
        logger.warning("Summary request rejected - missing or empty filename")
        raise HTTPException(
            status_code=400,
            detail="filename is required and cannot be empty.",
        )
    if not filename.lower().endswith(".pdf"):
        logger.warning(f"Summary request rejected - invalid filename: {filename}")
        raise HTTPException(
            status_code=400,
            detail="Invalid filename. Please specify a PDF file.",
        )
    # Look up the notebook
    notebook = await get_notebook_by_notebook_id(db, notebook_id.strip())
    if not notebook:
        logger.warning(f"Summary request rejected - notebook not found: {notebook_id}")
        raise HTTPException(
            status_code=404, detail=f"Notebook '{notebook_id}' not found"
        )
    logger.info(f"Found notebook: {notebook.title} (ID: {notebook.id})")
    # Verify PDF exists in notebook
    pdf = await get_pdf_by_filename_and_notebook(db, filename.strip(), notebook.id)
    if not pdf:
        logger.warning(
            f"Summary request rejected - PDF not found: {filename} in notebook {notebook_id}"
        )
        raise HTTPException(
            status_code=404,
            detail=f"PDF '{filename}' not found in notebook '{notebook_id}'",
        )
    logger.info(
        f"Found PDF: {filename} (ID: {pdf.id}, status: {pdf.processing_status})"
    )
    # Retrieve summary
    summary = await get_summary_by_source_name(db, filename.strip())
    if summary is None:
        logger.warning(f"Summary not found for PDF: {filename}")
        raise HTTPException(status_code=404, detail="Summary not found")
    logger.info(f"Successfully retrieved summary for {filename}")
    return {
        "summary": summary,
        "filename": filename.strip(),
        "notebook": notebook.title,
        "notebook_id": notebook.notebook_id,
    }
