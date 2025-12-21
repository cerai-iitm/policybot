import asyncio
import os
import uuid
from pathlib import Path

import aiofiles
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from src.config import cfg
from src.logger import logger
from src.rag import PDFProcessor
from src.schema.db import get_db
from src.schema.overall_summaries_crud import delete_overall_summaries_containing_file
from src.schema.source_summaries_crud import (
    delete_source_summary,
    get_summary_by_source_name,
)

router = APIRouter()


@router.get("/list")
async def list_pdfs():
    try:
        upload_dir = Path(cfg.DATA_DIR)
        # mkdir and iterdir are blocking filesystem ops; run them in a thread.
        await asyncio.to_thread(upload_dir.mkdir, exist_ok=True)

        def _list_pdfs():
            return [
                f.name
                for f in upload_dir.iterdir()
                if f.is_file() and f.suffix.lower() == ".pdf"
            ]

        pdf_files = await asyncio.to_thread(_list_pdfs)
        return JSONResponse(content={"pdfs": pdf_files}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list PDFs: {str(e)}")


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded.")

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400, detail="Invalid file format. Please upload a PDF."
        )

    upload_dir = Path(cfg.DATA_DIR)
    # Ensure directory exists (blocking) in a thread:
    await asyncio.to_thread(upload_dir.mkdir, exist_ok=True)
    file_path = upload_dir / file.filename

    try:
        # Use aiofiles for async file write
        async with aiofiles.open(file_path, "wb") as buffer:
            content = await file.read()
            await buffer.write(content)

        file_id = str(uuid.uuid4())
        return JSONResponse(
            status_code=201, content={"id": file_id, "filename": file.filename}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")


async def _delete_pdf_file(filename: str) -> bool:
    try:
        file_path = Path(cfg.DATA_DIR) / filename
        logger.info(f"Attempting to delete PDF file: {filename} from {file_path}")
        await asyncio.to_thread(os.remove, str(file_path))
        logger.info(f"Successfully deleted PDF file: {filename}")
        return True
    except FileNotFoundError:
        logger.warning(f"PDF file not found during deletion: {filename}")
        return False
    except PermissionError:
        logger.error(f"Permission denied when deleting file: {filename}")
        return False
    except Exception as e:
        logger.error(
            f"Unexpected error deleting file {filename}: {type(e).__name__} - {e}"
        )
        return False


@router.delete("/delete/{filename}")
async def delete_pdf(filename: str, db: AsyncSession = Depends(get_db)):
    """
    Delete a PDF and all associated data (file, embeddings, summaries).
    Runs all deletion operations in parallel for efficiency.
    """
    logger.info(f"Received delete request for PDF: {filename}")

    if not filename.lower().endswith(".pdf"):
        logger.warning(f"Invalid file format in delete request: {filename}")
        raise HTTPException(
            status_code=400,
            detail="Invalid file format. Please specify a PDF file to delete.",
        )

    file_path = Path(cfg.DATA_DIR) / filename
    exists = await asyncio.to_thread(file_path.exists)
    if not exists:
        logger.warning(f"Delete request for non-existent file: {filename}")
        raise HTTPException(status_code=404, detail="File not found.")

    try:
        logger.info(f"Starting parallel deletion operations for: {filename}")
        pdf_processor = PDFProcessor()

        # Run non-DB operations in parallel
        file_deleted, embeddings_deleted = await asyncio.gather(
            _delete_pdf_file(filename),
            pdf_processor.delete_embeddings(filename),
            return_exceptions=True,
        )

        # Run DB operations sequentially on the same session to avoid concurrent use
        summary_result = await delete_source_summary(db, filename)

        try:
            overall_deleted = await delete_overall_summaries_containing_file(
                db, filename
            )
        except Exception as overall_exc:
            # Ensure the session is clean for subsequent operations
            try:
                await db.rollback()
            except Exception:
                pass
            overall_deleted = overall_exc

        logger.info(f"Deletion operations completed for {filename}")
        logger.debug(
            "Results - File: %s, Embeddings: %s, Summary: %s, Overall summaries deleted: %s",
            file_deleted,
            embeddings_deleted,
            summary_result,
            overall_deleted,
        )

        # Log any failures but still return success if file was deleted
        failures = []
        if isinstance(file_deleted, Exception):
            logger.error(f"File deletion failed with exception: {file_deleted}")
            failures.append("file")
        elif not file_deleted:
            logger.error(f"File deletion returned False for: {filename}")
            failures.append("file")

        if isinstance(embeddings_deleted, Exception):
            logger.error(
                f"Embeddings deletion failed with exception: {embeddings_deleted}"
            )
            failures.append("embeddings")
        elif not embeddings_deleted:
            logger.warning(f"Embeddings deletion returned False for: {filename}")
            failures.append("embeddings")

        if isinstance(summary_result, Exception):
            logger.error(f"Summary deletion failed with exception: {summary_result}")
            failures.append("database summary")
        elif summary_result is None:
            logger.info(f"No summary found to delete for: {filename}")

        if isinstance(overall_deleted, Exception):
            logger.error(
                f"Overall summary deletion failed with exception: {overall_deleted}"
            )
            failures.append("overall summaries")
        elif isinstance(overall_deleted, int) and overall_deleted > 0:
            logger.info(
                f"Deleted {overall_deleted} overall summaries containing {filename}"
            )
        else:
            logger.info(
                f"No overall summaries contained {filename} or none were deleted"
            )

        if failures:
            logger.warning(
                f"Partial deletion for {filename}. Failed components: {', '.join(failures)}"
            )
        else:
            logger.info(f"Complete deletion successful for: {filename}")

        return JSONResponse(
            status_code=200,
            content={
                "message": f"File '{filename}' deleted.",
                "file_deleted": bool(file_deleted)
                and not isinstance(file_deleted, Exception),
                "embeddings_deleted": bool(embeddings_deleted)
                and not isinstance(embeddings_deleted, Exception),
                "summary_deleted": not isinstance(summary_result, Exception)
                and summary_result is not None,
                "overall_summaries_deleted": (
                    0
                    if isinstance(overall_deleted, Exception)
                    else int(overall_deleted) if isinstance(overall_deleted, int) else 0
                ),
            },
        )
    except Exception as e:
        logger.error(
            f"Unexpected error during deletion of {filename}: {type(e).__name__} - {str(e)}",
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")


@router.get("/process/{filename}")
async def process_uploaded_pdf(filename: str, db: AsyncSession = Depends(get_db)):
    pdf_processor = PDFProcessor()
    file_path = Path(cfg.DATA_DIR) / filename
    if not await asyncio.to_thread(file_path.exists):
        raise HTTPException(status_code=404, detail="File not found.")

    async def generate():
        logger.info(f"Starting processing for {file_path}")
        # Pass the async DB session into the processor so it can persist summaries
        async for update in pdf_processor.process_pdf(filename, db=db):
            yield f"data: {update}\n\n"
        yield "data: done\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.get("/view/{filename}")
async def view_pdf(filename: str):
    file_path = Path(cfg.DATA_DIR) / filename
    logger.info(f"Requested filename: {filename}")
    exists = await asyncio.to_thread(file_path.exists)
    if not exists or not filename.endswith(".pdf"):
        raise HTTPException(status_code=404, detail="PDF not found")
    return FileResponse(str(file_path), media_type="application/pdf", filename=filename)


@router.get("/summary/{filename}")
async def get_summary(filename: str, db: AsyncSession = Depends(get_db)):
    logger.info(f"Fetching summary for filename: {filename}")
    summary = await get_summary_by_source_name(db, filename)
    if summary is None:
        raise HTTPException(status_code=404, detail="Summary not found")
    return {"summary": summary}
