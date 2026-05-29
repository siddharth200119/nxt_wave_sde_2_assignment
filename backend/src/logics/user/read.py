from src.utils.database import get_db_cursor
from src.models.user import User
from uuid import UUID
from typing import Optional

def read_user(user_id: UUID, organization_id: UUID) -> Optional[User]:
    """
    Retrieves a user by user_id and organization_id.
    """
    with get_db_cursor() as cursor:
        cursor.execute(
            "SELECT * FROM users WHERE id = %s AND organization_id = %s",
            (user_id, organization_id)
        )
        result = cursor.fetchone()
        if result:
            return User.model_validate(result)
        return None
