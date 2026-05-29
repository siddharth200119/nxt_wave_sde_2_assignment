from src.utils.database import get_db_cursor
from src.models.user import User
from uuid import UUID
from typing import Optional

def get_user_by_email(email: str, organization_id: UUID) -> Optional[User]:
    """
    Retrieves a user by email and organization_id.
    """
    with get_db_cursor() as cursor:
        cursor.execute(
            "SELECT * FROM users WHERE email = %s AND organization_id = %s",
            (email, organization_id)
        )
        result = cursor.fetchone()
        if result:
            return User.model_validate(result)
        return None
