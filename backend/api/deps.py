# api/deps.py
from typing import Annotated
from fastapi import Depends
from fastapi_users import FastAPIUsers
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from core.security import auth_backend
from db.models.user import User


# Database dependency
async def get_user_db(session: AsyncSession = Depends(get_db)):
    from fastapi_users.db import SQLAlchemyUserDatabase

    yield SQLAlchemyUserDatabase(session, User)


# Create FastAPIUsers instance
fastapi_users = FastAPIUsers[User, int](
    get_user_db,
    [auth_backend],
)


# Get current authenticated user
async def get_current_user(
    user: User = Depends(fastapi_users.current_user),
) -> User:
    return user
