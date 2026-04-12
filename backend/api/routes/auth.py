# api/routes/auth.py
from fastapi import APIRouter, Request
from fastapi_users.schemas import BaseUser, BaseUserCreate
from pydantic import EmailStr

from api.deps import fastapi_users
from core.security import auth_backend
from db.models.user import User


class UserReadSchema(BaseUser):
    """Schema for reading user data."""


class UserCreateSchema(BaseUserCreate):
    """Schema for creating a user."""

    email: EmailStr
    full_name: str


router = APIRouter(prefix="/auth", tags=["auth"])

router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="",
    tags=["auth"],
)

router.include_router(
    fastapi_users.get_register_router(UserReadSchema, UserCreateSchema),
    prefix="",
    tags=["auth"],
)


@router.post("/logout")
async def logout(request: Request):
    """Logout endpoint - invalidates the token on client side."""
    return {"message": "Successfully logged out"}
