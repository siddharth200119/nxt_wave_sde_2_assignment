from fastapi import Request
from pydantic import BaseModel, Field, field_validator
from src.models import APIOutput, Route, Role, TaskPriority, TaskStatus
from src.logics import update_task
from uuid import UUID
from datetime import datetime, timezone
from typing import Optional
from src.logics.task.read import read_task
from src.logics.task.caching import invalidate_task_cache


class UpdateTaskRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None
    assignee_id: Optional[UUID] = None
    due_date: Optional[datetime] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not v.strip():
                raise ValueError("title cannot be empty or blank")
            return v.strip()
        return v

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v is not None:
            now = datetime.now(v.tzinfo or timezone.utc)
            if v <= now:
                raise ValueError("due_date must be in the future")
        return v


async def update_task_handler(request: Request, id: UUID, body: UpdateTaskRequest):
    try:
        user = request.state.user
        
        # Get only the fields that were explicitly set in the request JSON
        update_data = body.model_dump(exclude_unset=True)
        
         # Verify the task belongs to the user's organization first for security
        existing_task = read_task(task_id=id, organization_id=user.organization_id)
        if not existing_task:
            return APIOutput.failure(
                message="Task not found",
                status_code=404
            )

        # If user is a MEMBER, they can only update tasks assigned to them (SDE2 optimal guard)
        if user.role == Role.MEMBER and existing_task.assignee_id != user.id:
            return APIOutput.failure(
                message="Task not found",
                status_code=404
            )

        # If user is a MEMBER, they are only allowed to update the 'status' field.
        # Throw a 400 error if any other field is sent in the payload.
        if user.role == Role.MEMBER:
            forbidden_fields = [key for key in update_data.keys() if key != "status"]
            if forbidden_fields:
                return APIOutput.failure(
                    message=f"Members are only permitted to update the 'status' field. Invalid fields sent: {', '.join(forbidden_fields)}",
                    status_code=400
                )

        task = update_task(
            task_id=id,
            **update_data
        )
        
        if task:
            # Invalidate task list caches for this organization
            await invalidate_task_cache(organization_id=user.organization_id)

            return APIOutput.success(
                data=task.model_dump(mode="json"),
                message="Task updated successfully"
            )
        return APIOutput.failure(
            message="Task not found",
            status_code=404
        )
    except ValueError as e:
        return APIOutput.failure(message=str(e), status_code=400)
    except Exception as e:
        return APIOutput.failure(message=str(e), status_code=500)


route = Route(
    function=update_task_handler,
    path="/{id}",
    method="PATCH",
    required_roles=[Role.ADMIN, Role.MANAGER, Role.MEMBER],
    summary="Update a task",
    description="Updates task properties (title, description, priority, status, assignee, due_date) by ID"
)

