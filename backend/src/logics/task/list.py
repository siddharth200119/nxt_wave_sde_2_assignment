from src.utils.database import get_db_cursor
from src.models import Task, TaskPriority, TaskStatus, User, Organization
from uuid import UUID
from typing import Optional
import json
import math


def list_tasks(
    organization_id: UUID,
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    assignee_id: Optional[UUID] = None,
    page: int = 1,
    limit: int = 10
) -> dict:
    """
    Retrieves a paginated list of tasks matching the status, priority, and assignee filters
    within the specified organization.
    """
    # 1. Base conditions
    conditions = ["t.organization_id = %s"]
    params = [organization_id]
    
    # 2. Add filters dynamically
    if status is not None:
        conditions.append("t.status = %s")
        params.append(status.value)
        
    if priority is not None:
        conditions.append("t.priority = %s")
        params.append(priority.value)
        
    if assignee_id is not None:
        conditions.append("t.assignee_id = %s")
        params.append(assignee_id)
        
    where_clause = " WHERE " + " AND ".join(conditions)
    
    # 3. Calculate total count for metadata
    count_query = f"SELECT COUNT(*) as count FROM tasks t{where_clause}"
    
    # 4. Main query with joins, sorting, and pagination
    offset = (page - 1) * limit
    
    query = f"""
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
        {where_clause}
        ORDER BY t.created_at DESC
        LIMIT %s OFFSET %s
    """
    
    with get_db_cursor() as cursor:
        # Get count
        cursor.execute(count_query, tuple(params))
        total_count_row = cursor.fetchone()
        total_count = total_count_row["count"] if total_count_row else 0
        
        # Get paginated results
        query_params = params + [limit, offset]
        cursor.execute(query, tuple(query_params))
        results = cursor.fetchall() or []
        
        tasks = []
        for r in results:
            # Safe parsing for JSON/dict data
            org_data = r["organization_json"]
            if isinstance(org_data, str):
                org_data = json.loads(org_data)
                
            assignee_data = r["assignee_json"]
            if isinstance(assignee_data, str):
                assignee_data = json.loads(assignee_data)
                
            # Hydrate nested models
            org_model = Organization.model_validate(org_data) if org_data else None
            assignee_model = User.model_validate(assignee_data) if assignee_data else None
            
            task = Task(
                id=r["id"],
                organization_id=r["organization_id"],
                title=r["title"],
                description=r["description"],
                priority=TaskPriority(r["priority"]),
                status=TaskStatus(r["status"]),
                assignee_id=r["assignee_id"],
                due_date=r["due_date"],
                created_at=r["created_at"],
                updated_at=r["updated_at"],
                organization=org_model,
                assigned_to=assignee_model
            )
            tasks.append(task)
            
        total_pages = math.ceil(total_count / limit) if total_count > 0 else 0
        
        return {
            "tasks": tasks,
            "pagination": {
                "page": page,
                "limit": limit,
                "total_count": total_count,
                "total_pages": total_pages
            }
        }
