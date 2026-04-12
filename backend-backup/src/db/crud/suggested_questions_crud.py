"""CRUD operations for suggested questions."""

from typing import List, Optional
from uuid import uuid4

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..schema.suggested_questions import SuggestedQuestion


async def get_random_suggested_questions(
    db: AsyncSession,
    notebook_id: str,
    selected_filenames: Optional[List[str]] = None,
    limit: int = 3,
) -> List[dict]:
    """Get random suggested questions for a notebook, optionally filtered by filenames."""
    stmt = select(
        SuggestedQuestion.id,
        SuggestedQuestion.question,
        SuggestedQuestion.filename,
        SuggestedQuestion.notebook_id,
        SuggestedQuestion.created_at,
    ).where(SuggestedQuestion.notebook_id == notebook_id)

    # Filter by selected filenames if provided
    if selected_filenames:
        stmt = stmt.where(
            (SuggestedQuestion.filename.is_(None))
            | (SuggestedQuestion.filename.in_(selected_filenames))
        )
    else:
        # If no filenames selected, only return general questions (filename IS NULL)
        stmt = stmt.where(SuggestedQuestion.filename.is_(None))

    stmt = stmt.order_by(func.random()).limit(limit)
    res = await db.execute(stmt)
    rows = res.all()
    return [
        {
            "id": r[0],
            "question": r[1],
            "filename": r[2],
            "notebook_id": r[3],
            "created_at": r[4].isoformat() if r[4] is not None else None,
        }
        for r in rows
    ]


async def insert_suggested_question(
    db: AsyncSession,
    notebook_id: str,
    question: str,
    filename: Optional[str] = None,
) -> None:
    """Insert a suggested question for a notebook."""
    sq = SuggestedQuestion(
        id=str(uuid4()),
        notebook_id=notebook_id,
        question=question,
        filename=filename,
    )
    db.add(sq)
    await db.commit()
