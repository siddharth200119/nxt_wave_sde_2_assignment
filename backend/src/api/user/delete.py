from fastapi import Request
from src.models import APIOutput, Route, Role
from src.logics import delete_user
from uuid import UUID

async def delete_user_handler(request: Request, id: UUID):
    try:
        admin_user = request.state.user
        success = delete_user(user_id=id, organization_id=admin_user.organization_id)
        if success:
            return APIOutput.success(
                message="User deleted successfully"
            )
        return APIOutput.failure(
            message="User not found",
            status_code=404
        )
    except Exception as e:
        return APIOutput.failure(message=str(e), status_code=500)

route = Route(
    function=delete_user_handler,
    path="/{id}",
    method="DELETE",
    required_roles=[Role.ADMIN],
    summary="Delete a user",
    description="Deletes a user by ID within the administrator's organization"
)
