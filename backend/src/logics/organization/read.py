from src.utils.database import get_db_cursor
from src.models.organization import Organization
from uuid import UUID
from typing import Optional

def read_organization(org_id: UUID) -> Optional[Organization]:
    with get_db_cursor() as cursor:
        cursor.execute(
            "SELECT * FROM organizations WHERE id = %s",
            (org_id,)
        )
        result = cursor.fetchone()
        if result:
            return Organization.model_validate(result)
        return None
