from datetime import datetime, timedelta
from typing import Optional

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_config
from db.session import get_db
from db.models.user import User

config = get_config()

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = config.jwt_access_expire_minutes

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/policybot/api/auth/login")


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    sub: Optional[str] = None


class UserOut(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    is_active: bool
    is_demo_user: bool = False

    class Config:
        from_attributes = True


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def create_access_token(
    subject: str | int, expires_delta: Optional[timedelta] = None, is_demo: bool = False
) -> str:
    now = datetime.utcnow()
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "sub": str(subject),
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
        "is_demo": is_demo,
    }
    encoded_jwt = jwt.encode(to_encode, config.jwt_secret, algorithm=ALGORITHM)
    return encoded_jwt


def create_demo_token(user_id: int) -> str:
    """Create a non-expiring JWT for demo user."""
    now = datetime.utcnow()
    far_future = datetime.utcnow() + timedelta(days=365 * 10)
    to_encode = {
        "sub": str(user_id),
        "iat": int(now.timestamp()),
        "exp": int(far_future.timestamp()),
        "is_demo": True,
    }
    encoded_jwt = jwt.encode(to_encode, config.jwt_secret, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, config.jwt_secret, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired"
        ) from exc
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        ) from exc


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def get_user_by_username_or_email(
    db: AsyncSession, identity: str
) -> Optional[User]:
    result = await db.execute(select(User).where(User.username == identity))
    user = result.scalar_one_or_none()
    if user:
        return user
    result = await db.execute(select(User).where(User.email == identity))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    return await db.get(User, int(user_id))


async def create_user(
    db: AsyncSession,
    username: str,
    password: str,
    email: Optional[str] = None,
    full_name: Optional[str] = None,
) -> User:
    existing = await get_user_by_username(db, username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    if email:
        result = await db.execute(select(User).where(User.email == email))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
    hashed = get_password_hash(password)
    user = User(
        username=username,
        email=email,
        hashed_password=hashed,
        full_name=full_name,
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(
    db: AsyncSession, identity: str, password: str
) -> Optional[User]:
    user = await get_user_by_username_or_email(db, identity)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> User:
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload"
        )
    try:
        user = await get_user_by_id(db, int(user_id))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User lookup failed"
        ) from exc
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )
    is_active_val = user.is_active
    if isinstance(is_active_val, str):
        if str(is_active_val).lower() not in {"true", "1", "yes"}:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive user"
            )
    else:
        if not bool(is_active_val):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive user"
            )

    is_demo = payload.get("is_demo", False)
    user.is_demo_user = is_demo

    return user
