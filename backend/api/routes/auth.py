# api/routes/auth.py
from fastapi import APIRouter, Request
from fastapi_users import FastAPIUsers
from fastapi_users.schemas import BaseUser, BaseUserCreate
from pydantic import EmailStr

from core.security import auth_backend
from db.models.user import User
from api.deps import get_user_db


# Create FastAPIUsers instance with our backend
fastapi_users = FastAPIUsers[User, int](
    get_user_db,
    [auth_backend],
)


# Custom user schemas for fastapi-users
class UserReadSchema(BaseUser):
    """Schema for reading user data"""

    pass


class UserCreateSchema(BaseUserCreate):
    """Schema for creating a user"""

    email: EmailStr


# Include auth routers from fastapi-users
router = APIRouter(prefix="/auth", tags=["auth"])

router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/login",
    tags=["auth"],
)

router.include_router(
    fastapi_users.get_register_router(UserReadSchema, UserCreateSchema),
    prefix="/register",
    tags=["auth"],
)


# Optional: Add logout endpoint
@router.post("/logout")
async def logout(request: Request):
    """Logout endpoint - invalidates the token on client side"""
    return {"message": "Successfully logged out"}
