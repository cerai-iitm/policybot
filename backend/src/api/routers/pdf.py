import asyncio
import os
import traceback
from pathlib import Path

import aiofiles
from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
)
from fastapi import (
    Path as FastApiPath,
)
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from src.api.routers.pdf_schemas import (
    ErrorResponse,
    HTTPValidationError,
    PDFDeleteResponse,
    PDFListResponse,
    PDFSummaryResponse,
    PDFUploadResponse,
)
from sqlalchemy.ext.asyncio import AsyncSession

from src.core import cfg, logger
from src.db.config import AsyncSessionLocal
from src.db.crud import (
    delete_overall_summaries_containing_file,
    delete_source_summary,
    get_db,
    get_notebook_by_title,
    get_pdf_by_filename_and_notebook,
    get_pdfs_by_notebook,
    get_summary_by_source_name,
    delete_pdf as delete_pdf_record,
)
from src.services import PDFProcessor

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


async def _background_process_pdf(file_name: str, pdf_id: int) -> None:
    """Run PDF processing in background with a fresh DB session.

    This acquires a semaphore to bound concurrency and opens an independent
    AsyncSession so the request DB session can be closed immediately after upload.
    """
    await _PROCESS_SEMAPHORE.acquire()
    try:
        async with AsyncSessionLocal() as bg_db:
            pdf_processor = PDFProcessor()
            try:
                async for update in pdf_processor.process_pdf(
                    file_name, pdf_id=pdf_id, db=bg_db
                ):
                    logger.info(f"[bg:{pdf_id}] {update}")
            except Exception as e:
                logger.error(f"Background processing failed for {file_name}: {e}")
                logger.debug(traceback.format_exc())
                # attempt to mark the PDF as errored
                try:
                    from src.db.crud import update_pdf_status

                    await update_pdf_status(bg_db, pdf_id, "error")
                except Exception:
                    logger.exception(
                        "Failed to set PDF status to 'error' in background task"
                    )
    finally:
        _PROCESS_SEMAPHORE.release()


def _schedule_background_task_for_pdf(file_name: str, pdf_id: int) -> None:
    """Helper to schedule the background processing for a PDF.

    Tries to schedule on the running asyncio loop; falls back to a thread
    that creates its own event loop if necessary.
    """
    try:
        loop = asyncio.get_running_loop()
        task = loop.create_task(_background_process_pdf(file_name, pdf_id))

        def _on_task_done(t: asyncio.Task) -> None:
            try:
                exc = t.exception()
                if exc:
                    logger.error(f"Background task error for pdf_id={pdf_id}: {exc}")
            except asyncio.CancelledError:
                logger.info(f"Background task cancelled for pdf_id={pdf_id}")

        task.add_done_callback(_on_task_done)
        logger.info(
            f"Scheduled background processing for file: {file_name} (pdf_id={pdf_id})"
        )
    except RuntimeError:
        # No running event loop; fallback to a background thread with its own loop
        logger.warning(
            "No running event loop found; running background task in new loop thread (fallback)"
        )

        def _run_in_thread():
            import asyncio as _asyncio

            _loop = _asyncio.new_event_loop()
            _asyncio.set_event_loop(_loop)
            _loop.run_until_complete(_background_process_pdf(file_name, pdf_id))

        import threading

        threading.Thread(target=_run_in_thread, daemon=True).start()


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


@router.post(
    "/upload",
    response_model=PDFUploadResponse,
    status_code=201,
    summary="Upload PDF to notebook",
    description="""Upload a PDF file to a specific notebook.

**Processing States:**
- `uploaded`: File uploaded, processing not started
- `processing`: Text extraction and chunking in progress  
- `embeddings_complete`: Embeddings stored, summary pending
- `summary_generation`: Summary being generated
- `complete`: Fully processed

**Notes:**
- Only PDF files accepted (.pdf extension required)
- File names must be unique within a notebook
- Duplicate uploads return current processing state
- Notebook must exist before uploading
""",
    responses={
        201: {
            "description": "PDF uploaded successfully",
            "model": PDFUploadResponse,
        },
        200: {
            "description": "PDF already exists, returned current state",
            "model": PDFUploadResponse,
        },
        400: {
            "description": "Invalid input - missing file, invalid format, or missing notebook name",
            "model": ErrorResponse,
        },
        404: {
            "description": "Notebook not found",
            "model": ErrorResponse,
        },
        409: {
            "description": "PDF already fully processed",
            "model": ErrorResponse,
        },
        422: {
            "description": "Validation error",
            "model": HTTPValidationError,
        },
    },
)
async def upload_pdf(
    notebook_name: str = Form(
        ...,
        description="Name of the notebook (must exist)",
        example="My Notebook",
    ),
    file: UploadFile = File(
        ...,
        description="PDF file to upload",
        media_type="application/pdf",
    ),
    db: AsyncSession = Depends(get_db),
):
    """Upload a PDF file to a specific notebook."""
    logger.info(
        f"Upload request received - notebook: {notebook_name}, file: {file.filename}"
    )

    # Validate inputs
    if not file.filename:
        logger.warning("Upload rejected - no filename provided")
        raise HTTPException(status_code=400, detail="No file uploaded.")

    if not notebook_name:
        logger.warning("Upload rejected - no notebook name provided")
        raise HTTPException(status_code=400, detail="Notebook name is required.")

    if not file.filename.lower().endswith(".pdf"):
        logger.warning(f"Upload rejected - invalid file format: {file.filename}")
        raise HTTPException(
            status_code=400, detail="Invalid file format. Please upload a PDF."
        )

    # Step 1: Check if notebook exists
    notebook = await get_notebook_by_title(db, notebook_name)
    if not notebook:
        logger.warning(f"Upload rejected - notebook not found: {notebook_name}")
        raise HTTPException(
            status_code=404,
            detail=f"Notebook '{notebook_name}' not found. Create it first.",
        )

    logger.info(f"Found notebook: {notebook.title} (ID: {notebook.id})")

    # Step 2: Check processing state from database
    processing_state, existing_pdf = await _get_processing_state_from_db(
        file.filename, notebook.id, db
    )
    logger.info(f"Processing state for {file.filename}: {processing_state}")

    # Handle different processing states
    if processing_state == "complete":
        logger.info(f"File already fully processed: {file.filename}")
        return JSONResponse(
            status_code=409,
            content={
                "detail": "File already exists and is fully processed.",
                "filename": file.filename,
                "notebook": notebook_name,
                "processing_state": "complete",
            },
        )

    # If the PDF record exists and is in an error state, return an error and do not schedule
    if processing_state == "error":
        logger.error(
            f"PDF is in error state: {file.filename} (pdf id: {existing_pdf.id if existing_pdf else 'unknown'})"
        )
        return JSONResponse(
            status_code=500,
            content={
                "detail": "PDF is in error state. Please investigate and re-upload if needed.",
                "filename": file.filename,
                "notebook": notebook_name,
                "processing_state": "error",
            },
        )

    # For any other existing non-complete state (uploaded, processing, embeddings_complete, summary_generation),
    # schedule/resume background processing. The processor is idempotent and will skip already-done stages.
    if existing_pdf is not None:
        logger.info(
            f"Resuming/scheduling background processing for existing file: {file.filename} (state={processing_state})"
        )
        try:
            _schedule_background_task_for_pdf(file.filename, existing_pdf.id)
        except Exception as e:
            logger.error(
                f"Failed to schedule background task for existing PDF {file.filename}: {e}"
            )
            # Fallthrough to return a 500-like response
            return JSONResponse(
                status_code=500,
                content={
                    "detail": f"Failed to schedule processing: {str(e)}",
                    "filename": file.filename,
                    "notebook": notebook_name,
                    "processing_state": processing_state,
                },
            )

        return JSONResponse(
            status_code=200,
            content={
                "message": "Background processing scheduled/resumed for existing PDF.",
                "filename": file.filename,
                "notebook": notebook_name,
                "processing_state": processing_state,
            },
        )

    # Step 3: New file - proceed with upload
    logger.info(
        f"Proceeding with new file upload: {file.filename} to notebook: {notebook_name}"
    )

    try:
        # Create notebook folder structure
        upload_dir = Path(cfg.DATA_DIR) / notebook.notebook_id
        await asyncio.to_thread(upload_dir.mkdir, parents=True, exist_ok=True)

        file_path = upload_dir / file.filename
        logger.debug(f"Upload directory prepared: {upload_dir}")

        # Save file to disk
        async with aiofiles.open(file_path, "wb") as buffer:
            content = await file.read()
            await buffer.write(content)

        # Create PDF record in database
        relative_path = f"{notebook.notebook_id}/{file.filename}"
        pdf = await create_pdf(
            db=db,
            file_name=file.filename,
            file_path=relative_path,
            notebook_id=notebook.id,
        )

        logger.info(
            f"Successfully uploaded file and created DB record: {file.filename}"
        )
        # Schedule background processing so embeddings and summary are generated
        try:
            _schedule_background_task_for_pdf(file.filename, pdf.id)
        except Exception as e:
            logger.error(
                f"Failed to schedule background task for new PDF {file.filename}: {e}"
            )
        return JSONResponse(
            status_code=201,
            content={
                "filename": file.filename,
                "notebook": notebook_name,
                "notebook_id": notebook.notebook_id,
                "pdf_id": pdf.id,
                "processing_state": "uploaded",
                "file_path": relative_path,
            },
        )
    except Exception as e:
        logger.error(f"Failed to upload file {file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")


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
    notebook_name: str = Query(
        ...,
        description="Name of the notebook to list PDFs from",
        example="My Notebook",
    ),
    db: AsyncSession = Depends(get_db),
):
    """List all PDFs in a notebook with current processing status."""
    logger.info(f"List PDFs request for notebook: {notebook_name}")

    # Check if notebook exists
    notebook = await get_notebook_by_title(db, notebook_name)
    if not notebook:
        raise HTTPException(
            status_code=404, detail=f"Notebook '{notebook_name}' not found."
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
                "notebook": notebook_name,
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
    from src.schema.notebooks_crud import get_notebook_by_notebook_id

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


@router.delete(
    "/delete/{file_path:path}",
    response_model=PDFDeleteResponse,
    summary="Delete PDF (DELETE method)",
    description="""Delete a PDF and all associated data.

**Deletes:**
- PDF file from disk
- Embeddings from Qdrant vector store
- Summary from database
- PDF record from database
- Overall summaries containing this file

**Note:** Use full path format `{notebook_id}/{filename}`
""",
    responses={
        200: {
            "description": "PDF deleted successfully",
            "model": PDFDeleteResponse,
        },
        400: {
            "description": "Invalid file path or format",
            "model": ErrorResponse,
        },
        404: {
            "description": "Notebook or PDF not found",
            "model": ErrorResponse,
        },
    },
)
async def delete_pdf(
    file_path: str = FastApiPath(
        ...,
        description="Path to PDF in format: {notebook_id}/{filename}",
        example="nb_a1b2c3d4/document.pdf",
    ),
    db: AsyncSession = Depends(get_db),
):
    """Delete a PDF by its path."""
    logger.info(f"Delete request for: {file_path}")
    status_code, content = await _perform_deletion(file_path, db)
    return JSONResponse(status_code=status_code, content=content)


@router.post(
    "/remove",
    response_model=PDFDeleteResponse,
    summary="Delete PDF (POST method)",
    description="""Delete a PDF using POST method (firewall-friendly).

Same functionality as DELETE /delete/{file_path} but uses POST 
for environments where DELETE requests are blocked.
""",
    responses={
        200: {
            "description": "PDF deleted successfully",
            "model": PDFDeleteResponse,
        },
        400: {
            "description": "Invalid file path or format",
            "model": ErrorResponse,
        },
        404: {
            "description": "Notebook or PDF not found",
            "model": ErrorResponse,
        },
    },
)
async def remove_pdf(
    file_path: str = Form(
        ...,
        description="Path to PDF in format: {notebook_id}/{filename}",
        example="nb_a1b2c3d4/document.pdf",
    ),
    db: AsyncSession = Depends(get_db),
):
    """Remove a PDF by its path (POST for firewall compatibility)."""
    logger.info(f"Remove request for: {file_path}")
    status_code, content = await _perform_deletion(file_path, db)
    return JSONResponse(status_code=status_code, content=content)


@router.get(
    "/process/{file_path:path}",
    summary="Process PDF through RAG pipeline",
    description="""Process a PDF through the RAG (Retrieval-Augmented Generation) pipeline.

**Pipeline Stages:**
1. **Text Extraction**: Extract text from PDF pages
2. **Chunking**: Split text into semantic chunks
3. **Embedding**: Generate vector embeddings using AI model
4. **Storage**: Store embeddings in Qdrant vector database
5. **Summary**: Generate AI summary using LLM

**Returns:** Server-Sent Events (SSE) stream with real-time progress updates

**Status Tracking:**
- Processing status is saved to database after each stage
- Can be resumed if interrupted (checks existing embeddings/summaries)
- Status values: uploaded → processing → embeddings_complete → summary_generation → complete

**Example Events:**
```
data: Starting PDF processing...
data: Extracting text from PDF...
data: Running splitter for creating chunks...
data: Embedding chunks...
data: Saving embeddings to database...
data: Creating summary...
data: Summary created and saved.
data: PDF processing complete.
data: done
```
""",
    responses={
        200: {
            "description": "SSE stream of processing updates",
            "content": {
                "text/event-stream": {
                    "example": "data: Starting PDF processing...\n\ndata: done\n\n"
                }
            },
        },
        400: {
            "description": "Invalid file path format",
            "model": ErrorResponse,
        },
        404: {
            "description": "Notebook or PDF not found",
            "model": ErrorResponse,
        },
    },
)
async def process_uploaded_pdf(
    file_path: str = FastApiPath(
        ...,
        description="Path to PDF in format: {notebook_id}/{filename}",
        example="nb_a1b2c3d4/document.pdf",
    ),
    db: AsyncSession = Depends(get_db),
):
    """Process a PDF file using database state tracking."""
    logger.info(f"Process request for file: {file_path}")

    # Parse file_path to get notebook_id and filename
    parts = file_path.split("/")
    if len(parts) != 2:
        raise HTTPException(
            status_code=400,
            detail="Invalid file path. Expected format: {notebook_id}/{filename}",
        )

    notebook_id_str, filename = parts

    # Look up the notebook
    from src.schema.notebooks_crud import get_notebook_by_notebook_id

    notebook = await get_notebook_by_notebook_id(db, notebook_id_str)
    if not notebook:
        raise HTTPException(
            status_code=404, detail=f"Notebook '{notebook_id_str}' not found"
        )

    # Look up the PDF record
    pdf = await get_pdf_by_filename_and_notebook(db, filename, notebook.id)
    if not pdf:
        raise HTTPException(
            status_code=404,
            detail=f"PDF '{filename}' not found in notebook '{notebook_id_str}'",
        )

    # Check file exists on disk
    full_path = Path(cfg.DATA_DIR) / file_path
    if not await asyncio.to_thread(full_path.exists):
        logger.error(f"File exists in DB but not on disk: {file_path}")
        raise HTTPException(status_code=404, detail="File not found on disk.")

    logger.info(
        f"Processing PDF: {filename} (ID: {pdf.id}) in notebook: {notebook.title}"
    )

    async def generate():
        pdf_processor = PDFProcessor()
        logger.info(f"Starting processing for {file_path} with state tracking")

        # Pass pdf_id so processor can update status
        async for update in pdf_processor.process_pdf(filename, pdf_id=pdf.id, db=db):
            yield f"data: {update}\n\n"
        yield "data: done\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.get(
    "/view/{file_path:path}",
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
        404: {
            "description": "PDF not found",
            "model": ErrorResponse,
        },
    },
)
async def view_pdf(
    file_path: str = FastApiPath(
        ...,
        description="Path to PDF in format: {notebook_id}/{filename}",
        example="nb_a1b2c3d4/document.pdf",
    ),
):
    """View a PDF file."""
    full_path = Path(cfg.DATA_DIR) / file_path
    logger.info(f"View request for: {file_path}")

    exists = await asyncio.to_thread(full_path.exists)
    if not exists or not file_path.endswith(".pdf"):
        raise HTTPException(status_code=404, detail="PDF not found")

    filename = os.path.basename(file_path)
    return FileResponse(str(full_path), media_type="application/pdf", filename=filename)


@router.get(
    "/summary/{file_path:path}",
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
            "description": "Invalid file path format",
            "model": ErrorResponse,
        },
        404: {
            "description": "Notebook, PDF, or summary not found",
            "model": ErrorResponse,
        },
    },
)
async def get_summary(
    file_path: str = FastApiPath(
        ...,
        description="Path to PDF in format: {notebook_id}/{filename}",
        example="nb_a1b2c3d4/document.pdf",
    ),
    db: AsyncSession = Depends(get_db),
):
    """Get the summary for a processed PDF."""
    logger.info(f"Fetching summary for: {file_path}")

    # Parse file_path to get notebook_id and filename
    parts = file_path.split("/")
    if len(parts) != 2:
        raise HTTPException(
            status_code=400,
            detail="Invalid file path. Expected format: {notebook_id}/{filename}",
        )

    notebook_id_str, filename = parts

    # Look up the notebook
    from src.schema.notebooks_crud import get_notebook_by_notebook_id

    notebook = await get_notebook_by_notebook_id(db, notebook_id_str)
    if not notebook:
        raise HTTPException(
            status_code=404, detail=f"Notebook '{notebook_id_str}' not found"
        )

    # Verify PDF exists in notebook
    pdf = await get_pdf_by_filename_and_notebook(db, filename, notebook.id)
    if not pdf:
        raise HTTPException(
            status_code=404,
            detail=f"PDF '{filename}' not found in notebook '{notebook_id_str}'",
        )

    summary = await get_summary_by_source_name(db, filename)
    if summary is None:
        raise HTTPException(status_code=404, detail="Summary not found")

    return {
        "summary": summary,
        "filename": filename,
        "notebook": notebook.title,
        "notebook_id": notebook.notebook_id,
    }
