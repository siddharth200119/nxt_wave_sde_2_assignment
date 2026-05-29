import os
import secrets
import jwt
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4
from typing import Optional, Tuple
from fastapi import HTTPException, status
from src.models import Role
from src.utils.database import get_db_cursor
from src.utils.hasher import hash_string


JWT_SECRET = os.getenv("JWT_SECRET", "default_jwt_secret_please_change_in_production")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 2
REFRESH_TOKEN_EXPIRE_DAYS = 7


def create_access_token(user_id: UUID, organization_id: UUID, role: Role) -> str:
    """
    Generates a signed JWT access token containing user info, valid for 2 hours.
    """
    expire = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    payload = {
        "sub": str(user_id),
        "org_id": str(organization_id),
        "role": role.value,
        "exp": expire
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_access_token(token: str) -> dict:
    """
    Decodes and verifies a JWT access token.
    Raises HTTPException 401 if invalid or expired.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "status": 401,
                "code": "UNAUTHORIZED",
                "message": "Access token has expired"
            }
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "status": 401,
                "code": "UNAUTHORIZED",
                "message": "Invalid access token"
            }
        )


def create_refresh_token(user_id: UUID) -> str:
    """
    Generates a secure random refresh token, hashes it,
    records it in the refresh_tokens table, and returns the raw token.
    """
    raw_token = "rfr_" + secrets.token_hex(32)
    token_hash = hash_string(raw_token)
    token_id = uuid4()
    expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    with get_db_cursor() as cursor:
        cursor.execute(
            "INSERT INTO refresh_tokens (id, user_id, token_hash, expires_at) "
            "VALUES (%s, %s, %s, %s)",
            (token_id, user_id, token_hash, expires_at)
        )
    
    return raw_token
