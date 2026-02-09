"""CRUD operations for PDFs."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.schema.pdfs import PDF


async def get_pdf_by_filename_and_notebook(
    db: AsyncSession, file_name: str, notebook_id: int
) -> Optional[PDF]:
    """Get a PDF by its filename and notebook ID."""
    result = await db.execute(
        select(PDF).where(PDF.file_name == file_name, PDF.notebook_id == notebook_id)
    )
    return result.scalar_one_or_none()


async def get_pdf_by_id(db: AsyncSession, pdf_id: int) -> Optional[PDF]:
    """Get a PDF by its ID."""
    result = await db.execute(select(PDF).where(PDF.id == pdf_id))
    return result.scalar_one_or_none()


async def create_pdf(
    db: AsyncSession, file_name: str, file_path: str, notebook_id: int
) -> PDF:
    """Create a new PDF record."""
    pdf = PDF(
        file_name=file_name,
        file_path=file_path,
        notebook_id=notebook_id,
        processing_status="uploaded",
    )
    db.add(pdf)
    await db.commit()
    await db.refresh(pdf)
    return pdf


async def update_pdf_status(
    db: AsyncSession, pdf_id: int, status: str
) -> Optional[PDF]:
    """Update the processing status of a PDF."""
    pdf = await get_pdf_by_id(db, pdf_id)
    if pdf:
        pdf.processing_status = status
        await db.commit()
        await db.refresh(pdf)
    return pdf


async def delete_pdf(db: AsyncSession, pdf_id: int) -> bool:
    """Delete a PDF by ID. Returns True if deleted."""
    pdf = await get_pdf_by_id(db, pdf_id)
    if pdf:
        await db.delete(pdf)
        await db.commit()
        return True
    return False


async def get_pdfs_by_notebook(db: AsyncSession, notebook_id: int):
    """Get all PDFs belonging to a notebook."""
    result = await db.execute(select(PDF).where(PDF.notebook_id == notebook_id))
    return result.scalars().all()
