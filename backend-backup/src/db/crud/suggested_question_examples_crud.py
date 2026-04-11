"""CRUD operations for suggested question example answers."""

from typing import Optional
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..schema.suggested_question_examples import SuggestedQuestionExample


async def get_example_for_suggested_question(
    db: AsyncSession, suggested_question_id: str
) -> Optional[dict]:
    """Return the example answer for a given suggested question id, or None."""
    stmt = select(
        SuggestedQuestionExample.id,
        SuggestedQuestionExample.suggested_question_id,
        SuggestedQuestionExample.example_answer,
        SuggestedQuestionExample.created_at,
    ).where(SuggestedQuestionExample.suggested_question_id == suggested_question_id)

    res = await db.execute(stmt)
    row = res.first()
    if not row:
        return None
    return {
        "id": row[0],
        "suggested_question_id": row[1],
        "example_answer": row[2],
        "created_at": row[3].isoformat() if row[3] is not None else None,
    }


async def insert_example_answer(
    db: AsyncSession, suggested_question_id: str, example_answer: str
) -> None:
    """Insert an example answer for a suggested question."""
    e = SuggestedQuestionExample(
        id=str(uuid4()),
        suggested_question_id=suggested_question_id,
        example_answer=example_answer,
    )
    db.add(e)
    await db.commit()
