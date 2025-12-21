from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.schema.source_summaries import SourceSummary


async def add_source_summary(
    db: AsyncSession, source_name: str, summary: str
) -> Optional[SourceSummary]:
    new_summary = SourceSummary(source_name=source_name, summary=summary)
    db.add(new_summary)
    try:
        await db.commit()
        await db.refresh(new_summary)
        return new_summary
    except IntegrityError:
        await db.rollback()
        # return existing if insertion collided
        stmt = select(SourceSummary).where(SourceSummary.source_name == source_name)
        res = await db.execute(stmt)
        existing = res.scalars().first()
        return existing


async def delete_source_summary(
    db: AsyncSession, source_name: str
) -> Optional[SourceSummary]:
    stmt = select(SourceSummary).where(SourceSummary.source_name == source_name)
    res = await db.execute(stmt)
    summary = res.scalars().first()
    if summary:
        db.delete(summary)
        await db.commit()
        return summary
    return None


async def get_summary_by_source_name(db: AsyncSession, file_name: str) -> Optional[str]:
    stmt = select(SourceSummary).where(SourceSummary.source_name == file_name)
    res = await db.execute(stmt)
    summary_obj = res.scalars().first()
    if summary_obj:
        return str(summary_obj.summary)
    return None


async def get_all_source_summaries(db: AsyncSession) -> List[SourceSummary]:
    stmt = select(SourceSummary)
    res = await db.execute(stmt)
    return list(res.scalars().all())
