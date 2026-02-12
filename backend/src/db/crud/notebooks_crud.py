"""CRUD operations for notebooks."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..schema import Notebook


async def get_notebook_by_title(db: AsyncSession, title: str) -> Optional[Notebook]:
    """Get a notebook by its title."""
    result = await db.execute(select(Notebook).where(Notebook.title == title))
    return result.scalar_one_or_none()


async def get_notebook_by_id(db: AsyncSession, notebook_id: int) -> Optional[Notebook]:
    """Get a notebook by its ID."""
    result = await db.execute(select(Notebook).where(Notebook.id == notebook_id))
    return result.scalar_one_or_none()


async def create_notebook(
    db: AsyncSession, title: str, description: Optional[str] = None
) -> Notebook:
    """Create a new notebook."""
    import secrets

    # Generate a unique notebook_id (like nb_abc123)
    notebook_id = f"nb_{secrets.token_hex(8)}"

    notebook = Notebook(notebook_id=notebook_id, title=title, description=description)
    db.add(notebook)
    await db.commit()
    await db.refresh(notebook)
    return notebook


async def list_notebooks(db: AsyncSession):
    """List all notebooks."""
    result = await db.execute(select(Notebook))
    return result.scalars().all()


async def delete_notebook(db: AsyncSession, notebook_id: int) -> bool:
    """Delete a notebook by ID. Returns True if deleted."""
    notebook = await get_notebook_by_id(db, notebook_id)
    if notebook:
        await db.delete(notebook)
        await db.commit()
        return True
    return False
