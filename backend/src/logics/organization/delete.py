from src.utils.database import get_db_cursor
from uuid import UUID

def delete_organization(org_id: UUID) -> bool:
    with get_db_cursor() as cursor:
        cursor.execute(
            "DELETE FROM organizations WHERE id = %s",
            (org_id,)
        )
        return cursor.rowcount > 0
