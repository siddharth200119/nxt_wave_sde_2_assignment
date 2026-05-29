from fastapi import Request
from src.models import APIOutput, Route, Role
from src.logics import list_users

async def list_users_handler(request: Request):
    try:
        current_user = request.state.user
        users = list_users(organization_id=current_user.organization_id)
        safe_users = [u.safe_json() for u in users]
        return APIOutput.success(
            data=safe_users,
            message="Users retrieved successfully"
        )
    except Exception as e:
        return APIOutput.failure(message=str(e), status_code=500)

route = Route(
    function=list_users_handler,
    method="GET",
    required_roles=[Role.ADMIN, Role.MANAGER],
    summary="List all users",
    description="Returns a list of all users within the authenticated user's organization"
)
