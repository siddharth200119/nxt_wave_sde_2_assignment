from src.utils.database import get_db_cursor
from uuid import UUID

def delete_user(user_id: UUID, organization_id: UUID) -> bool:
    """
    Deletes a user belonging to the organization.
    Returns True if deletion was successful, False otherwise.
    """
    with get_db_cursor() as cursor:
        cursor.execute(
            "DELETE FROM users WHERE id = %s AND organization_id = %s RETURNING 1",
            (user_id, organization_id)
        )
        result = cursor.fetchone()
        return result is not None
