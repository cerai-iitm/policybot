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
from src.schema.source_summaries_crud import get_summary_by_source_name

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


@router.delete("/delete/{filename}")
async def delete_pdf(filename: str):
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Invalid file format. Please specify a PDF file to delete.",
        )

    file_path = Path(cfg.DATA_DIR) / filename
    exists = await asyncio.to_thread(file_path.exists)
    if not exists:
        raise HTTPException(status_code=404, detail="File not found.")

    try:
        # Remove file in a thread to avoid blocking the event loop
        await asyncio.to_thread(os.remove, str(file_path))
        return JSONResponse(
            status_code=200, content={"message": f"File '{filename}' deleted."}
        )
    except Exception as e:
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
