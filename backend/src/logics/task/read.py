from src.utils.database import get_db_cursor
from src.models import Task, TaskPriority, TaskStatus, User, Organization
from uuid import UUID
from typing import Optional
import json


def read_task(task_id: UUID, organization_id: UUID) -> Optional[Task]:
    """
    Retrieves a task by task_id and organization_id using a single SQL query
    with JOINs and PostgreSQL JSON formatting (json_build_object) to hydrate relations.
    """
    query = """
        SELECT 
            t.id,
            t.organization_id,
            t.title,
            t.description,
            t.priority,
            t.status,
            t.assignee_id,
            t.due_date,
            t.created_at,
            t.updated_at,
            json_build_object(
                'id', o.id,
                'name', o.name,
                'created_at', o.created_at,
                'updated_at', o.updated_at
            ) AS organization_json,
            CASE 
                WHEN t.assignee_id IS NOT NULL THEN
                    json_build_object(
                        'id', u.id,
                        'organization_id', u.organization_id,
                        'email', u.email,
                        'password_hash', u.password_hash,
                        'role', u.role,
                        'is_active', u.is_active,
                        'created_at', u.created_at,
                        'updated_at', u.updated_at
                    )
                ELSE NULL
            END AS assignee_json
        FROM tasks t
        LEFT JOIN organizations o ON t.organization_id = o.id
        LEFT JOIN users u ON t.assignee_id = u.id
        WHERE t.id = %s AND t.organization_id = %s
    """
    with get_db_cursor() as cursor:
        cursor.execute(query, (task_id, organization_id))
        task_record = cursor.fetchone()
        if not task_record:
            return None

        # Safe parsing for JSON/dict data
        org_data = task_record["organization_json"]
        if isinstance(org_data, str):
            org_data = json.loads(org_data)
            
        assignee_data = task_record["assignee_json"]
        if isinstance(assignee_data, str):
            assignee_data = json.loads(assignee_data)

        # Hydrate nested Pydantic models
        org_model = Organization.model_validate(org_data) if org_data else None
        assignee_model = User.model_validate(assignee_data) if assignee_data else None

        return Task(
            id=task_record["id"],
            organization_id=task_record["organization_id"],
            title=task_record["title"],
            description=task_record["description"],
            priority=TaskPriority(task_record["priority"]),
            status=TaskStatus(task_record["status"]),
            assignee_id=task_record["assignee_id"],
            due_date=task_record["due_date"],
            created_at=task_record["created_at"],
            updated_at=task_record["updated_at"],
            organization=org_model,
            assigned_to=assignee_model
        )
