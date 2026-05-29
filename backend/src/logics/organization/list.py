from src.utils.database import get_db_cursor
from src.models.organization import Organization
from typing import List

def list_organizations() -> List[Organization]:
    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM organizations ORDER BY created_at DESC")
        results = cursor.fetchall()
        return [Organization.model_validate(row) for row in results]
