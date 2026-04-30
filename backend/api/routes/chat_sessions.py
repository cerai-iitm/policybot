# api/routes/chat_sessions.py
import secrets
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from api.deps import get_current_user
from api.schemas.chat_session import (
    ChatSessionCreate,
    ChatSessionResponse,
    ChatSessionListResponse,
)
from db.models import User, Notebook, ChatSession
from db.session import get_db

router = APIRouter(prefix="/chat/sessions", tags=["ChatSessions"])


async def get_notebook_for_user(
    notebook_id: str, user_id: int, db: AsyncSession
) -> Notebook:
    result = await db.execute(
        select(Notebook).where(
            and_(Notebook.notebook_id == notebook_id, Notebook.user_id == user_id)
        )
    )
    notebook = result.scalar_one_or_none()
    if not notebook:
        raise HTTPException(status_code=404, detail="Notebook not found")
    return notebook


async def get_session_for_user(
    session_id: str, user_id: int, db: AsyncSession
) -> ChatSession:
    result = await db.execute(
        select(ChatSession).where(
            and_(ChatSession.session_id == session_id, ChatSession.user_id == user_id)
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.post(
    "", response_model=ChatSessionResponse, status_code=status.HTTP_201_CREATED
)
async def create_session(
    request: ChatSessionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    notebook = await get_notebook_for_user(request.notebook_id, current_user.id, db)

    result = await db.execute(
        select(ChatSession).where(
            and_(
                ChatSession.notebook_id == notebook.id,
                ChatSession.is_active == True,
            )
        )
    )
    existing_active = result.scalar_one_or_none()
    if existing_active:
        existing_active.is_active = False

    session = ChatSession(
        session_id=f"session_{secrets.token_hex(8)}",
        notebook_id=notebook.id,
        user_id=current_user.id,
        title=request.title,
        is_active=True,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)

    return ChatSessionResponse(
        id=session.id,
        session_id=session.session_id,
        notebook_id=request.notebook_id,
        title=session.title,
        is_active=session.is_active,
        created_at=session.created_at,
        updated_at=session.updated_at,
    )


@router.get("/active/{notebook_id}", response_model=ChatSessionResponse)
async def get_active_session(
    notebook_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    notebook = await get_notebook_for_user(notebook_id, current_user.id, db)

    result = await db.execute(
        select(ChatSession).where(
            and_(
                ChatSession.notebook_id == notebook.id,
                ChatSession.is_active == True,
            )
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="No active session found")

    return ChatSessionResponse(
        id=session.id,
        session_id=session.session_id,
        notebook_id=notebook_id,
        title=session.title,
        is_active=session.is_active,
        created_at=session.created_at,
        updated_at=session.updated_at,
    )


@router.get("", response_model=ChatSessionListResponse)
async def list_sessions(
    notebook_id: str = Query(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    notebook = await get_notebook_for_user(notebook_id, current_user.id, db)

    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.notebook_id == notebook.id)
        .order_by(ChatSession.created_at.desc())
    )
    sessions = result.scalars().all()

    return ChatSessionListResponse(
        sessions=[
            ChatSessionResponse(
                id=s.id,
                session_id=s.session_id,
                notebook_id=notebook_id,
                title=s.title,
                is_active=s.is_active,
                created_at=s.created_at,
                updated_at=s.updated_at,
            )
            for s in sessions
        ]
    )


@router.put("/{session_id}/activate", response_model=ChatSessionResponse)
async def activate_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    session = await get_session_for_user(session_id, current_user.id, db)

    result = await db.execute(
        select(ChatSession).where(
            and_(
                ChatSession.notebook_id == session.notebook_id,
                ChatSession.is_active == True,
                ChatSession.id != session.id,
            )
        )
    )
    other_active = result.scalars().all()
    for other in other_active:
        other.is_active = False

    session.is_active = True
    await db.commit()
    await db.refresh(session)

    notebook_result = await db.get(Notebook, session.notebook_id)
    notebook_external_id = notebook_result.notebook_id if notebook_result else ""

    return ChatSessionResponse(
        id=session.id,
        session_id=session.session_id,
        notebook_id=notebook_external_id,
        title=session.title,
        is_active=session.is_active,
        created_at=session.created_at,
        updated_at=session.updated_at,
    )


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    session = await get_session_for_user(session_id, current_user.id, db)
    await db.delete(session)
    await db.commit()
