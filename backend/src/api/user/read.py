from fastapi import Request
from src.models import APIOutput, Route, Role
from src.logics import read_user
from uuid import UUID

async def read_user_handler(request: Request, id: UUID):
    try:
        admin_user = request.state.user
        user = read_user(user_id=id, organization_id=admin_user.organization_id)
        if user:
            return APIOutput.success(
                data=user.safe_json(),
                message="User retrieved successfully"
            )
        return APIOutput.failure(
            message="User not found",
            status_code=404
        )
    except Exception as e:
        return APIOutput.failure(message=str(e), status_code=500)

route = Route(
    function=read_user_handler,
    path="/{id}",
    method="GET",
    required_roles=[Role.ADMIN],
    summary="Get user details",
    description="Returns a user's details by ID within the administrator's organization"
)
