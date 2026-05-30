from fastapi import Request
from pydantic import BaseModel, Field, field_validator
from src.models import APIOutput, Route, Role, TaskPriority
from src.logics import create_task
from src.logics.task.caching import invalidate_task_cache
from uuid import UUID
from datetime import datetime, timezone
from typing import Optional


class CreateTaskRequest(BaseModel):
    title: str = Field(..., min_length=1, description="Task title (required)")
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee_id: Optional[UUID] = None
    due_date: Optional[datetime] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("title is required and cannot be empty or blank")
        return v.strip()

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v is not None:
            now = datetime.now(v.tzinfo or timezone.utc)
            if v <= now:
                raise ValueError("due_date must be in the future")
        return v


async def create_task_handler(request: Request, body: CreateTaskRequest):
    try:
        user = request.state.user
        task = create_task(
            organization_id=user.organization_id,
            title=body.title,
            description=body.description,
            priority=body.priority,
            assignee_id=body.assignee_id,
            due_date=body.due_date
        )
        # Invalidate task list caches for this organization
        await invalidate_task_cache(organization_id=user.organization_id)

        return APIOutput.success(
            data=task.model_dump(mode="json"),
            message="Task created successfully",
            status_code=201
        )
    except ValueError as e:
        return APIOutput.failure(message=str(e), status_code=400)
    except Exception as e:
        return APIOutput.failure(message=str(e), status_code=500)


route = Route(
    function=create_task_handler,
    path="/",
    method="POST",
    required_roles=[Role.ADMIN, Role.MANAGER],
    summary="Create a new task",
    description="Creates a new task within the administrator's or manager's organization"
)
