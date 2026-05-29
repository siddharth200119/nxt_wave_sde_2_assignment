from src.utils.database import get_db_cursor
from src.models.organization import Organization
from uuid import uuid4

def create_organization(name: str) -> Organization:
    with get_db_cursor() as cursor:
        org_id = uuid4()
        cursor.execute(
            "INSERT INTO organizations (id, name) VALUES (%s, %s) RETURNING *",
            (org_id, name)
        )
        result = cursor.fetchone()
        return Organization.model_validate(result)
