# core/security.py
import pwdlib
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.password import PasswordHelper

from app.config import get_config

config = get_config()

# Argon2 password hasher (using pwdlib with recommended settings - Argon2 by default)
password_helper = PasswordHelper(password_hash=pwdlib.PasswordHash.recommended())

# JWT Transport (bearer token)
bearer_transport = BearerTransport(tokenUrl="/policybot/api/auth/login")

# JWT Strategy
jwt_strategy = JWTStrategy(
    secret=config.jwt_secret,
    lifetime_seconds=config.jwt_access_expire_minutes * 60,
)

# Authentication Backend
auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=lambda: jwt_strategy,
)
