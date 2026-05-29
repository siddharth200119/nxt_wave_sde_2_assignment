from typing import Tuple
from src.utils.database import get_db_cursor
from src.utils.hasher import hash_string
from src.models.user import User
from src.models.role import Role
from src.utils.auth import create_access_token, create_refresh_token
from src.logics.user.get_by_email import get_user_by_email
from src.logics.organization.read import read_organization
from uuid import uuid4, UUID


def register_user(organization_id: UUID, email: str, password: str, role: Role = Role.MEMBER) -> Tuple[User, str, str]:
    """
    Checks if the organization exists, verifies email uniqueness, hashes password, 
    saves the new user, generates tokens, and returns (User, access_token, refresh_token).
    """
    # 1. Check if organization exists
    org = read_organization(organization_id)
    if not org:
        raise ValueError("Organization does not exist")

    # 2. Check if user already exists
    existing_user = get_user_by_email(email, organization_id)
    if existing_user:
        raise ValueError("User with this email already exists in the organization")

    # 3. Hash password and save user
    password_hash = hash_string(password)
    user_id = uuid4()
    
    with get_db_cursor() as cursor:
        cursor.execute(
            "INSERT INTO users (id, organization_id, email, password_hash, role) "
            "VALUES (%s, %s, %s, %s, %s) RETURNING *",
            (user_id, organization_id, email, password_hash, role.value)
        )
        result = cursor.fetchone()
        user = User.model_validate(result)

    # 4. Generate tokens
    access_token = create_access_token(user.id, user.organization_id, user.role)
    refresh_token = create_refresh_token(user.id)
    
    return user, access_token, refresh_token
