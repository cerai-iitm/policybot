from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.crud import (
    create_notebook as crud_create_notebook,
)
from src.db.crud import get_notebook_by_title
from src.db.crud import (
    list_notebooks as crud_list_notebooks,
)


async def create_notebook(db: AsyncSession, title: str, description: Optional[str]):
    """Create a notebook and return a serializable dict matching the Pydantic model."""
    existing = await get_notebook_by_title(db, title)
    if existing:
        raise HTTPException(
            status_code=409, detail=f"Notebook with title '{title}' already exists." 
        )

    nb = await crud_create_notebook(db, title=title, description=description)

    return {
        "id": nb.id,
        "notebook_id": nb.notebook_id,
        "title": nb.title,
        "description": nb.description,
        "created_at": nb.created_at.isoformat(),
    }


async def list_notebooks(db: AsyncSession) -> List[dict]:
    nbs = await crud_list_notebooks(db)
    out = []
    for nb in nbs:
        out.append(
            {
                "id": nb.id,
                "notebook_id": nb.notebook_id,
                "title": nb.title,
                "description": nb.description,
                "created_at": nb.created_at.isoformat(),
            }
        )
    return out
