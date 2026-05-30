from src.utils.database import get_db_cursor
from uuid import UUID


def delete_task(task_id: UUID, organization_id: UUID) -> bool:
    """
    Deletes a task by task_id and organization_id.
    Returns True if successfully deleted, False otherwise.
    """
    with get_db_cursor() as cursor:
        cursor.execute(
            "DELETE FROM tasks WHERE id = %s AND organization_id = %s RETURNING id",
            (task_id, organization_id)
        )
        result = cursor.fetchone()
        return result is not None
