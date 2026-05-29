from src.utils.database import get_db_cursor
from src.models.user import User
from uuid import UUID

def list_users(organization_id: UUID) -> list[User]:
    """
    Retrieves all users belonging to the organization.
    """
    with get_db_cursor() as cursor:
        cursor.execute(
            "SELECT * FROM users WHERE organization_id = %s ORDER BY created_at DESC",
            (organization_id,)
        )
        results = cursor.fetchall()
        return [User.model_validate(r) for r in results]
