from fastapi import Request
from src.models import APIOutput, Route, Role
from src.logics import delete_task
from uuid import UUID


async def delete_task_handler(request: Request, id: UUID):
    try:
        user = request.state.user
        success = delete_task(task_id=id, organization_id=user.organization_id)
        if success:
            return APIOutput.success(
                message="Task deleted successfully"
            )
        return APIOutput.failure(
            message="Task not found",
            status_code=404
        )
    except Exception as e:
        return APIOutput.failure(message=str(e), status_code=500)


route = Route(
    function=delete_task_handler,
    path="/{id}",
    method="DELETE",
    required_roles=[Role.ADMIN, Role.MANAGER],
    summary="Delete a task",
    description="Deletes a task by ID within the administrator's or manager's organization"
)
