# api/routes/notebooks.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import secrets

from api.deps import get_current_user
from db.session import get_db
from db.models import User, Notebook
from api.schemas.notebook import NotebookCreate, NotebookResponse, NotebookListResponse

router = APIRouter(prefix="/notebooks", tags=["notebooks"])


@router.post("", response_model=NotebookResponse, status_code=status.HTTP_201_CREATED)
async def create_notebook(
    notebook_data: NotebookCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    notebook = Notebook(
        notebook_id=f"nb_{secrets.token_hex(8)}",
        user_id=current_user.id,
        title=notebook_data.title,
        description=notebook_data.description,
    )
    db.add(notebook)
    await db.commit()
    await db.refresh(notebook)
    return notebook


@router.get("", response_model=NotebookListResponse)
async def list_notebooks(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Notebook).where(Notebook.user_id == current_user.id)
    )
    notebooks = result.scalars().all()
    return {"notebooks": notebooks}


@router.get("/{notebook_id}", response_model=NotebookResponse)
async def get_notebook(
    notebook_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Notebook).where(
            Notebook.notebook_id == notebook_id, Notebook.user_id == current_user.id
        )
    )
    notebook = result.scalar_one_or_none()
    if not notebook:
        raise HTTPException(status_code=404, detail="Notebook not found")
    return notebook


@router.delete("/{notebook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notebook(
    notebook_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Notebook).where(
            Notebook.notebook_id == notebook_id, Notebook.user_id == current_user.id
        )
    )
    notebook = result.scalar_one_or_none()
    if not notebook:
        raise HTTPException(status_code=404, detail="Notebook not found")
    await db.delete(notebook)
    await db.commit()
