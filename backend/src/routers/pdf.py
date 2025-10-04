import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from sqlalchemy.orm import Session

from src.config import cfg
from src.logger import logger
from src.rag import PDFProcessor
from src.schema.source_summaries_crud import get_summary_by_source_name

router = APIRouter()
pdf_processor = PDFProcessor()


def get_db():
    db = cfg.DB_SESSION
    try:
        yield db
    finally:
        db.close()


@router.get("/list")
async def list_pdfs():
    try:
        upload_dir = Path(cfg.DATA_DIR)
        upload_dir.mkdir(exist_ok=True)

        pdf_files = [
            f.name
            for f in upload_dir.iterdir()
            if f.is_file() and f.suffix.lower() == ".pdf"
        ]
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
    upload_dir.mkdir(exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)
    if os.path.exists(file_path):
        raise HTTPException(status_code=409, detail="File already exists.")

    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

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

    file_path = os.path.join(cfg.DATA_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found.")

    try:
        os.remove(file_path)
        return JSONResponse(
            status_code=200, content={"message": f"File '{filename}' deleted."}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")


@router.get("/process/{filename}")
async def process_uploaded_pdf(filename: str):
    file_path = Path(cfg.DATA_DIR) / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found.")

    async def generate():
        async for update in pdf_processor.process_pdf(str(file_path)):
            yield f"data: {update}\n\n"
        yield "data: done\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.get("/view/{filename}")
async def view_pdf(filename: str):
    file_path = os.path.join(cfg.DATA_DIR, filename)
    logger.info(f"Requested filename: {filename}")
    logger.info(f"Full file path: {file_path}")
    logger.info(f"File exists: {os.path.exists(file_path)}")
    if not os.path.exists(file_path) or not filename.endswith(".pdf"):
        raise HTTPException(status_code=404, detail="PDF not found")
    return FileResponse(file_path, media_type="application/pdf", filename=filename)


@router.get("/summary/{filename}")
def get_summary(filename: str, db: Session = Depends(get_db)):
    summary = get_summary_by_source_name(db, filename)
    if summary is None:
        raise HTTPException(status_code=404, detail="Summary not found")
    return {"summary": summary}
