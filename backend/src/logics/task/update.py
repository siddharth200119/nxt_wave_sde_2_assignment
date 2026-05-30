from src.utils.database import get_db_cursor
from src.models import Task, TaskPriority, TaskStatus
from src.logics.task.read import read_task
from uuid import UUID
from datetime import datetime
from typing import Optional, Any


def update_task(
    task_id: UUID,
    **kwargs: Any
) -> Optional[Task]:
    """
    Dynamically updates a task by task_id.
    Performs assignee validation if assignee_id is updated.
    Returns the fully hydrated, updated Task model using a single roundtrip join query.
    """
    valid_fields = {"title", "description", "priority", "status", "assignee_id", "due_date"}
    update_data = {k: v for k, v in kwargs.items() if k in valid_fields}

    with get_db_cursor() as cursor:
        # First, retrieve the task's existing organization_id to handle validation and retrieval isolation
        cursor.execute("SELECT organization_id FROM tasks WHERE id = %s", (task_id,))
        record = cursor.fetchone()
        if not record:
            return None
        organization_id = record["organization_id"]

        if not update_data:
            # No fields to update, just return the existing task
            return read_task(task_id, organization_id)

        # 1. Validation: If assignee_id is being updated and is not None, verify they belong to same org and are active
        if "assignee_id" in update_data and update_data["assignee_id"] is not None:
            assignee_id = update_data["assignee_id"]
            cursor.execute(
                "SELECT is_active FROM users WHERE id = %s AND organization_id = %s",
                (assignee_id, organization_id)
            )
            user_record = cursor.fetchone()
            if not user_record:
                raise ValueError("Assignee must belong to the same organization")
            if not user_record["is_active"]:
                raise ValueError("Assignee account is currently deactivated")

        # 2. Build and execute dynamic update query
        fields = []
        values = []
        for k, v in update_data.items():
            fields.append(f"{k} = %s")
            if hasattr(v, "value"):
                values.append(v.value)
            else:
                values.append(v)
        
        values.append(task_id)
        query = f"UPDATE tasks SET {', '.join(fields)}, updated_at = NOW() WHERE id = %s RETURNING id"
        cursor.execute(query, tuple(values))
        task_record = cursor.fetchone()
        
        if not task_record:
            return None

    # 3. Retrieve fully hydrated Task model with a single SQL query (JOINs + JSON formatting)
    return read_task(task_id, organization_id)

