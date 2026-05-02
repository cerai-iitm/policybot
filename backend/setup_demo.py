#!/usr/bin/env python3
"""
Demo setup script - creates demo user, notebooks, and PDF records.
Run this after migrations are complete (called from entrypoint.sh).
"""

import asyncio
import logging
import shutil
import uuid
from pathlib import Path
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import get_config
from core.auth import get_password_hash
from db.models.notebook import Notebook
from db.models.pdf import PDF
from db.models.user import User
from services.pdf_processor import PDFProcessor
from demo_config import DEMO_USER, DEMO_NOTEBOOKS, DEMO_PDF_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def process_pdf_background(pdf_id: int, processor: PDFProcessor):
    """Process a single PDF - embeddings, summary, suggested queries."""
    from db.session import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        try:
            async for update in processor.process_pdf(pdf_id, db):
                logger.info(f"[PDF {pdf_id}] {update}")
                if isinstance(update, str) and update.startswith("Error:"):
                    logger.error(f"[PDF {pdf_id}] Error detected, stopping processing")
                    break
        except Exception as e:
            logger.exception(f"Background processing failed for pdf_id {pdf_id}")


async def setup_demo(db: AsyncSession) -> List[int]:
    """Setup demo user, notebooks, and PDF records. Returns list of PDF IDs to process."""
    config = get_config()

    demo_username = DEMO_USER["username"]
    demo_password = DEMO_USER["password"]
    demo_email = DEMO_USER.get("email")
    demo_full_name = DEMO_USER.get("full_name")

    result = await db.execute(select(User).where(User.username == demo_username))
    demo_user = result.scalar_one_or_none()

    if not demo_user:
        logger.info(f"Creating demo user: {demo_username}")
        hashed = get_password_hash(demo_password)
        demo_user = User(
            username=demo_username,
            email=demo_email,
            full_name=demo_full_name,
            hashed_password=hashed,
            is_active=True,
            is_demo_user=True,
        )
        db.add(demo_user)
        await db.commit()
        await db.refresh(demo_user)
        logger.info(f"Demo user created with ID: {demo_user.id}")
    else:
        logger.info(f"Demo user already exists: {demo_username} (ID: {demo_user.id})")

    pdf_ids_to_process = []

    for nb_config in DEMO_NOTEBOOKS:
        notebook_id = f"nb_{nb_config['notebook_id']}"
        result = await db.execute(
            select(Notebook).where(
                Notebook.notebook_id == notebook_id, Notebook.user_id == demo_user.id
            )
        )
        notebook = result.scalar_one_or_none()

        if not notebook:
            logger.info(f"Creating notebook: {notebook_id}")
            notebook = Notebook(
                notebook_id=notebook_id,
                user_id=demo_user.id,
                title=nb_config["title"],
                description=nb_config["description"],
            )
            db.add(notebook)
            await db.commit()
            await db.refresh(notebook)
            logger.info(f"Notebook created: {notebook_id}")
        else:
            logger.info(f"Notebook already exists: {notebook_id}")

        pdf_filenames = nb_config["pdfs"]
        for pdf_filename in pdf_filenames:
            result = await db.execute(
                select(PDF).where(
                    PDF.notebook_id == notebook.id,
                    PDF.original_filename == pdf_filename,
                    PDF.user_id == demo_user.id,
                )
            )
            existing_pdf = result.scalar_one_or_none()

            if existing_pdf:
                logger.info(f"PDF already exists: {pdf_filename}")
                if existing_pdf.processing_status != "complete":
                    pdf_ids_to_process.append(existing_pdf.id)
                    logger.info(
                        f"  Queuing incomplete PDF for processing: {pdf_filename}"
                    )
                continue

            src_path = Path(DEMO_PDF_DIR) / pdf_filename
            if not src_path.exists():
                logger.warning(f"PDF file not found: {src_path}")
                continue

            stored_filename = str(uuid.uuid4())
            upload_path = Path(config.upload_dir) / str(demo_user.id) / str(notebook.id)
            upload_path.mkdir(parents=True, exist_ok=True)

            dst_filename = f"{stored_filename}.pdf"
            dst_path = upload_path / dst_filename

            try:
                shutil.copy2(src_path, dst_path)
                logger.info(f"Copied PDF: {pdf_filename} -> {dst_path}")
            except Exception as e:
                logger.error(f"Failed to copy PDF {pdf_filename}: {e}")
                continue

            relative_path = f"{demo_user.id}/{notebook.id}/{dst_filename}"

            pdf = PDF(
                user_id=demo_user.id,
                notebook_id=notebook.id,
                original_filename=pdf_filename,
                stored_filename=stored_filename,
                file_path=relative_path,
                processing_status="uploaded",
            )
            db.add(pdf)
            await db.commit()
            await db.refresh(pdf)
            logger.info(f"PDF record created: {pdf_filename} (ID: {pdf.id})")

            pdf_ids_to_process.append(pdf.id)
            logger.info(f"  PDF queued for processing: {pdf_filename} (ID: {pdf.id})")

    return pdf_ids_to_process


async def process_all_pdfs(pdf_ids: List[int]):
    """Process all PDFs in parallel."""
    if not pdf_ids:
        logger.info("No PDFs to process")
        return

    logger.info(f"Processing {len(pdf_ids)} PDFs...")

    processor = PDFProcessor()

    tasks = [process_pdf_background(pdf_id, processor) for pdf_id in pdf_ids]
    await asyncio.gather(*tasks)

    logger.info(f"All {len(pdf_ids)} PDFs processed!")


async def main():
    config = get_config()
    engine = create_async_engine(config.database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        pdf_ids = await setup_demo(db)

    await process_all_pdfs(pdf_ids)

    logger.info("Demo setup complete!")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
