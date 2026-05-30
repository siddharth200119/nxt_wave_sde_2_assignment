from src.utils.database import get_db_cursor
from src.models import Task, TaskPriority
from src.logics.task.read import read_task
from uuid import UUID
from datetime import datetime
from typing import Optional


def create_task(
    organization_id: UUID,
    title: str,
    description: Optional[str],
    priority: TaskPriority,
    assignee_id: Optional[UUID],
    due_date: Optional[datetime]
) -> Task:
    """
    Creates a task inside the database and returns a fully hydrated Task model
    using a single roundtrip join query.
    """
    with get_db_cursor() as cursor:
        # 1. Validation: If assignee_id is provided, verify they are active in the same organization
        if assignee_id is not None:
            cursor.execute(
                "SELECT is_active FROM users WHERE id = %s AND organization_id = %s",
                (assignee_id, organization_id)
            )
            user_record = cursor.fetchone()
            if not user_record:
                raise ValueError("Assignee must belong to the same organization")
            if not user_record["is_active"]:
                raise ValueError("Assignee account is currently deactivated")

        # 2. Insert the task
        cursor.execute(
            "INSERT INTO tasks (organization_id, title, description, priority, status, assignee_id, due_date) "
            "VALUES (%s, %s, %s, %s, 'TODO', %s, %s) "
            "RETURNING id",
            (
                organization_id,
                title,
                description,
                priority.value,
                assignee_id,
                due_date
            )
        )
        task_record = cursor.fetchone()
        task_id = task_record["id"]

    # 3. Retrieve fully hydrated Task model with a single SQL query (JOINs + JSON formatting)
    task_model = read_task(task_id, organization_id)
    if not task_model:
        raise RuntimeError("Failed to retrieve created task details")
    
    return task_model
