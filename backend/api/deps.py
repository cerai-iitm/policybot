# api/deps.py
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi_users import FastAPIUsers
from fastapi_users.db.base import BaseUserDatabase
from fastapi_users.manager import BaseUserManager
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import jwt

from app.config import get_config
from core.security import auth_backend
from db.models.user import User
from db.session import get_db

config = get_config()
bearer_scheme = HTTPBearer(auto_error=True)


class SQLAlchemyUserDatabase(BaseUserDatabase[User, int]):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, id: int) -> User | None:
        return await self.session.get(User, id)

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_oauth_account(self, oauth: str, account_id: str) -> User | None:
        return None

    async def create(self, create_dict: dict) -> User:
        user = User(**create_dict)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update(self, user: User, update_dict: dict) -> User:
        for key, value in update_dict.items():
            if hasattr(user, key):
                setattr(user, key, value)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def delete(self, user: User) -> None:
        await self.session.delete(user)
        await self.session.commit()

    async def add_oauth_account(self, user: User, create_dict: dict) -> User:
        return user

    async def update_oauth_account(
        self, user: User, oauth_account: object, update_dict: dict
    ) -> User:
        return user


class UserManager(BaseUserManager[User, int]):
    def parse_id(self, value: str) -> int:
        return int(value)


async def get_user_db(session: AsyncSession = Depends(get_db)):
    yield SQLAlchemyUserDatabase(session)


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)


fastapi_users = FastAPIUsers[User, int](get_user_manager, [auth_backend])


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    session: AsyncSession = Depends(get_db),
) -> User:
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            config.jwt_secret,
            algorithms=["HS256"],
            audience="fastapi-users:auth",
        )
    except Exception as exc:
        print("JWT_DECODE_ERROR", type(exc).__name__, str(exc))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        ) from exc

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )

    try:
        user = await session.get(User, int(user_id))
    except Exception as exc:
        print("USER_LOOKUP_ERROR", type(exc).__name__, str(exc))
        raise
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )

    if str(user.is_active).lower() not in {"true", "1", "yes"}:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )

    return user
