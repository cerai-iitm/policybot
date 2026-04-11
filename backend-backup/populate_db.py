#!/usr/bin/env python3
"""
Script to create 3 notebooks and upload/process multiple PDFs into the first notebook, populating the database with test data.
Replaces shell scripts for cross-OS compatibility.

First creates 3 notebooks:
- Notebook 1: Description for notebook 1
- Notebook 2: Description for notebook 2
- Notebook 3: Description for notebook 3

Then uploads PDFs to Notebook 1 (or specified title).

Usage:
    python populate_db.py [--pdf-dir PATH] [--notebook-title TITLE]

Defaults:
    --pdf-dir: folder (relative to backend/)
    --notebook-title: Notebook 1
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Add backend/src to path for imports
backend_dir = Path(__file__).parent
src_dir = backend_dir / "src"
sys.path.insert(0, str(src_dir))

from src.core import cfg
from src.db import get_db
from src.db.crud import (
    create_pdf,
    update_pdf_status,
)
from src.db.crud.notebooks_crud import get_notebook_by_title
from src.services.notebooks import create_notebook
from src.services.pdf_processor import PDFProcessor


async def main():
    parser = argparse.ArgumentParser(
        description="Create 3 notebooks and upload/process multiple PDFs into the first notebook to populate the database."
    )
    parser.add_argument(
        "--pdf-dir",
        type=str,
        default="pdfs",
        help="Directory containing PDF files to upload (relative to backend/, default: folder)",
    )
    parser.add_argument(
        "--notebook-title",
        type=str,
        default="Notebook 1",
        help="Title for the notebook to upload PDFs to (default: Notebook 1)",
    )
    args = parser.parse_args()

    pdf_dir = Path(args.pdf_dir)
    if not pdf_dir.exists():
        print(f"Error: PDF directory not found at {pdf_dir}")
        sys.exit(1)

    pdf_files = list(pdf_dir.glob("*.pdf"))
    if not pdf_files:
        print(f"Error: No PDF files found in {pdf_dir}")
        sys.exit(1)

    notebook_title = args.notebook_title

    print(f"Processing {len(pdf_files)} PDFs from: {pdf_dir}")
    print(f"Notebook title: {notebook_title}")

    async for db in get_db():
        try:
            # Create 3 notebooks first
            print("Creating 3 notebooks...")
            notebooks_data = [
                {"title": "Notebook 1", "description": "Description for notebook 1"},
                {"title": "Notebook 2", "description": "Description for notebook 2"},
                {"title": "Notebook 3", "description": "Description for notebook 3"},
            ]
            for nb_data in notebooks_data:
                notebook = await create_notebook(
                    db, title=nb_data["title"], description=nb_data["description"]
                )
                print(
                    f"Created notebook: {notebook['notebook_id']} - {nb_data['title']}"
                )

            # Now proceed with PDF processing for the specified notebook
            # Get or create notebook
            print("Checking for existing notebook...")
            existing_notebook = await get_notebook_by_title(db, notebook_title)
            if existing_notebook:
                notebook = existing_notebook
                notebook_id_str = notebook.notebook_id
                notebook_id_int = notebook.id
                print(f"Using existing notebook: {notebook_id_str}")
            else:
                print("Creating new notebook...")
                notebook = await create_notebook(
                    db,
                    title=notebook_title,
                    description="Auto-populated notebook with multiple PDFs",
                )
                notebook_id_str = notebook["notebook_id"]
                notebook_id_int = notebook["id"]
                print(f"Created notebook: {notebook_id_str}")

            # Process each PDF sequentially
            for pdf_path in pdf_files:
                print(f"\nProcessing PDF: {pdf_path}")
                with open(pdf_path, "rb") as f:
                    pdf_content = f.read()

                # Save PDF file to data directory
                print("Saving PDF file...")
                save_dir = Path(cfg.DATA_DIR) / str(notebook_id_str)
                save_dir.mkdir(parents=True, exist_ok=True)
                file_path = save_dir / pdf_path.name
                with open(file_path, "wb") as f:
                    f.write(pdf_content)
                print(f"Saved PDF to: {file_path}")

                # Create PDF record
                print("Creating PDF record...")
                pdf_record = await create_pdf(
                    db,
                    file_name=pdf_path.name,
                    file_path=f"{notebook_id_str}/{pdf_path.name}",
                    notebook_id=notebook_id_int,
                )
                pdf_id = pdf_record.id
                print(f"Created PDF record: {pdf_id}")

                # Process PDF
                print("Processing PDF...")
                processor = PDFProcessor()
                docs = await asyncio.to_thread(
                    processor._extract_text_from_pdf,
                    f"{notebook_id_str}/{pdf_path.name}",
                )
                if not docs:
                    raise Exception(f"Failed to extract text from PDF {pdf_path.name}")

                split_docs = await asyncio.to_thread(
                    processor._run_splitter, docs, pdf_path.name
                )
                if not split_docs:
                    raise Exception(f"Failed to split documents for {pdf_path.name}")

                embeddings = await asyncio.to_thread(
                    processor._embed_docs, split_docs, pdf_path.name
                )
                if embeddings is None:
                    raise Exception(
                        f"Failed to generate embeddings for {pdf_path.name}"
                    )

                await processor._store_embeddings(split_docs, embeddings, pdf_path.name)
                await update_pdf_status(db, pdf_id, "embeddings_complete")

                # Generate and add summary
                print("Generating summary...")
                await processor._create_summary(docs, pdf_path.name, db=db)
                await update_pdf_status(db, pdf_id, "complete")

                print(f"Completed processing PDF: {pdf_path.name}")

            print("\nAll PDFs processed successfully!")
            print(f"Notebook ID: {notebook_id_str}")

        except Exception as e:
            print(f"Error: {e}")
            await db.rollback()
            sys.exit(1)
        finally:
            await db.close()


if __name__ == "__main__":
    asyncio.run(main())
