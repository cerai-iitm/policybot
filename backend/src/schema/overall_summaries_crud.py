import hashlib
import json
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from src.schema.overall_summaries import OverallSummary


def _hash_filenames(file_names: List[str]) -> str:
    sorted_names = sorted(file_names)
    key_str = "|".join(sorted_names)
    return hashlib.sha256(key_str.encode("utf-8")).hexdigest()


async def add_overall_summary(
    db: AsyncSession, file_names: List[str], summary: str
) -> OverallSummary:
    pdf_set_hash = _hash_filenames(file_names)
    pdf_file_names_json = json.dumps(sorted(file_names))
    new_summary = OverallSummary(
        pdf_set_hash=pdf_set_hash, pdf_file_names=pdf_file_names_json, summary=summary
    )
    db.add(new_summary)
    try:
        await db.commit()
        await db.refresh(new_summary)
        return new_summary
    except IntegrityError:
        await db.rollback()
        existing = await get_overall_summary(db, file_names)
        if existing:
            return existing
        raise


async def get_overall_summary(
    db: AsyncSession, file_names: List[str]
) -> Optional[OverallSummary]:
    pdf_set_hash = _hash_filenames(file_names)
    stmt = select(OverallSummary).filter_by(pdf_set_hash=pdf_set_hash)
    res = await db.execute(stmt)
    return res.scalars().first()


async def delete_overall_summary(db: AsyncSession, file_names: List[str]) -> bool:
    pdf_set_hash = _hash_filenames(file_names)
    stmt = select(OverallSummary).filter_by(pdf_set_hash=pdf_set_hash)
    res = await db.execute(stmt)
    summary = res.scalars().first()
    if summary:
        db.delete(summary)
        await db.commit()
        return True
    return False


async def delete_overall_summaries_containing_file(
    db: AsyncSession, file_name: str
) -> int:
    """
    Delete all overall summaries where the deleted file was part of the summary set.

    Returns the number of summaries deleted.
    """
    stmt = select(OverallSummary)
    res = await db.execute(stmt)
    summaries = res.scalars().all()

    to_delete = []
    for summary in summaries:
        try:
            file_list = json.loads(summary.pdf_file_names)
        except Exception:
            file_list = []
        if file_name in file_list:
            to_delete.append(summary)

    deleted = 0
    if to_delete:
        for summary in to_delete:
            db.delete(summary)
            deleted += 1
        await db.commit()

    return deleted
