from typing import Optional, Tuple
from src.utils.database import get_db_cursor
from src.utils.hasher import hash_string
from src.models.user import User
from src.utils.auth import create_access_token, create_refresh_token
from src.logics.organization.read import read_organization
from uuid import UUID


def login_user(email: str, password: str, organization_id: UUID) -> Tuple[Optional[User], Optional[str], Optional[str]]:
    """
    Checks if the organization exists, verifies credentials, 
    generates access & refresh tokens, and returns (User, access_token, refresh_token).
    """
    # 1. Check if organization exists
    org = read_organization(organization_id)
    if not org:
        raise ValueError("Organization does not exist")

    # 2. Check credentials
    password_hash = hash_string(password)
    
    with get_db_cursor() as cursor:
        cursor.execute(
            "SELECT * FROM users WHERE email = %s AND organization_id = %s AND password_hash = %s",
            (email, organization_id, password_hash)
        )
        result = cursor.fetchone()
        if result:
            user = User.model_validate(result)
            access_token = create_access_token(user.id, user.organization_id, user.role)
            refresh_token = create_refresh_token(user.id)
            return user, access_token, refresh_token
        return None, None, None
