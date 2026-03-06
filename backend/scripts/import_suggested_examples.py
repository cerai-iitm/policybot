#!/usr/bin/env python3
"""Import suggested questions and example answers from a JSON file.

JSON format: a list of objects with keys:
  - notebook_id: string (notebook.notebook_id)
  - question: string
  - filename: optional string
  - example_answer: string

Usage:
  python import_suggested_examples.py examples.json
"""
import argparse
import asyncio
import json
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parents[1]
src_dir = backend_dir / "src"
sys.path.insert(0, str(src_dir))

from src.db import get_db
from src.db.crud import insert_suggested_question
from src.db.crud.suggested_question_examples_crud import insert_example_answer
from src.db.schema.suggested_questions import SuggestedQuestion
from sqlalchemy import select


async def main():
    parser = argparse.ArgumentParser(description="Import suggested examples from JSON")
    parser.add_argument("json_file", help="Path to JSON file")
    args = parser.parse_args()

    p = Path(args.json_file)
    if not p.exists():
        print(f"File not found: {p}")
        return

    data = json.loads(p.read_text())
    if not isinstance(data, list):
        print("JSON must be a list of entries")
        return

    async for db in get_db():
        try:
            for i, item in enumerate(data, start=1):
                nb = item.get("notebook_id")
                question = item.get("question")
                filename = item.get("filename")
                example = item.get("example_answer")

                if not nb or not question or not example:
                    print(f"Skipping entry #{i}: missing required fields")
                    continue

                print(f"Inserting suggested question for notebook={nb}: '{question[:60]}'")
                await insert_suggested_question(db, nb, question, filename=filename)

                # retrieve the inserted suggested question id (most recent match)
                # include filename exactly as provided (NULL-safe)
                if filename is None:
                    stmt = (
                        select(SuggestedQuestion.id)
                        .where(
                            SuggestedQuestion.notebook_id == nb,
                            SuggestedQuestion.question == question,
                            SuggestedQuestion.filename.is_(None),
                        )
                        .order_by(SuggestedQuestion.created_at.desc())
                        .limit(1)
                    )
                else:
                    stmt = (
                        select(SuggestedQuestion.id)
                        .where(
                            SuggestedQuestion.notebook_id == nb,
                            SuggestedQuestion.question == question,
                            SuggestedQuestion.filename == filename,
                        )
                        .order_by(SuggestedQuestion.created_at.desc())
                        .limit(1)
                    )
                res = await db.execute(stmt)
                row = res.scalar_one_or_none()
                if not row:
                    print(f"Warning: inserted question not found for '{question[:60]}'")
                    continue
                suggested_id = row
                print(f"  -> inserted id: {suggested_id}")

                print(f"  Inserting example answer (len={len(example)})")
                await insert_example_answer(db, suggested_id, example)

            print("Import complete")
        except Exception as e:
            print(f"Error during import: {e}")
            await db.rollback()
            raise
        finally:
            await db.close()


if __name__ == "__main__":
    asyncio.run(main())
