# api/deps.py
from fastapi import Depends
from fastapi_users import FastAPIUsers
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import auth_backend
from db.models.user import User
from db.session import get_db
from fastapi_users.db.base import BaseUserDatabase


class SQLAlchemyUserDatabase(BaseUserDatabase[User, int]):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, id: int) -> User | None:
        return await self.session.get(User, id)

    async def get_by_email(self, email: str) -> User | None:
        from sqlalchemy import select

        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_oauth_account(self, oauth: str, account_id: str) -> User | None:
        return None

    def _to_dict(self, data):
        """Convert Pydantic model or dict to plain dict."""
        if hasattr(data, "model_dump"):
            return data.model_dump()
        elif hasattr(data, "dict"):
            return data.dict()
        return dict(data)

    async def create(
        self, create_dict: dict, safe: bool = True, request: object = None
    ) -> User:
        # Convert to dict if it's a Pydantic model
        data = self._to_dict(create_dict)

        # Handle password -> hashed_password mapping
        if "password" in data:
            data["hashed_password"] = data.pop("password")

        # Ensure full_name is always set (required field)
        if "full_name" not in data or not data["full_name"]:
            data["full_name"] = data.get("email", "User").split("@")[0]

        # Ensure is_active is string
        if "is_active" in data:
            if isinstance(data["is_active"], bool):
                data["is_active"] = "true" if data["is_active"] else "false"

        # Build user dict with only valid fields
        user_dict = {
            "email": str(data.get("email", "")),
            "hashed_password": str(data.get("hashed_password", "")),
            "full_name": str(data.get("full_name", "User")),
            "is_active": str(data.get("is_active", "true")),
        }

        user = User(**user_dict)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update(
        self, user: User, update_dict: dict, safe: bool = True, request: object = None
    ) -> User:
        # Convert to dict if it's a Pydantic model
        data = self._to_dict(update_dict)

        for key in ["email", "hashed_password", "full_name", "is_active"]:
            if key in data:
                value = data[key]
                if key == "is_active" and isinstance(value, bool):
                    value = "true" if value else "false"
                if hasattr(user, key):
                    setattr(user, key, value)
        self.session.add(user)
        await self.session.commit()
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


# Database dependency
async def get_user_db(session: AsyncSession = Depends(get_db)):
    yield SQLAlchemyUserDatabase(session)


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
