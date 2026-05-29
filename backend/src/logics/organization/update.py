from src.utils.database import get_db_cursor
from src.models.organization import Organization
from uuid import UUID
from typing import Optional

def update_organization(org_id: UUID, name: str) -> Optional[Organization]:
    with get_db_cursor() as cursor:
        cursor.execute(
            "UPDATE organizations SET name = %s, updated_at = NOW() WHERE id = %s RETURNING *",
            (name, org_id)
        )
        result = cursor.fetchone()
        if result:
            return Organization.model_validate(result)
        return None
