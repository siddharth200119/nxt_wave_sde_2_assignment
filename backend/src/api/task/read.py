from fastapi import Request
from src.models import APIOutput, Route, Role
from src.logics import read_task
from uuid import UUID


async def read_task_handler(request: Request, id: UUID):
    try:
        user = request.state.user
        task = read_task(task_id=id, organization_id=user.organization_id)
        if task:
            # If user is a MEMBER, they can only retrieve tasks assigned to them (SDE2 optimal guard)
            if user.role == Role.MEMBER and task.assignee_id != user.id:
                return APIOutput.failure(
                    message="Task not found",
                    status_code=404
                )

            return APIOutput.success(
                data=task.model_dump(mode="json"),
                message="Task retrieved successfully"
            )
        return APIOutput.failure(
            message="Task not found",
            status_code=404
        )
    except Exception as e:
        return APIOutput.failure(message=str(e), status_code=500)


route = Route(
    function=read_task_handler,
    path="/{id}",
    method="GET",
    required_roles=[Role.ADMIN, Role.MANAGER, Role.MEMBER],
    summary="Get task details",
    description="Returns a task's details by ID within the user's organization"
)
