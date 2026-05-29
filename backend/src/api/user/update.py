from fastapi import Request
from pydantic import BaseModel, EmailStr
from src.models import APIOutput, Route, Role
from src.logics import update_user
from uuid import UUID
from typing import Optional

class UpdateUserRequest(BaseModel):
    email: Optional[EmailStr] = None
    role: Optional[Role] = None
    is_active: Optional[bool] = None

async def update_user_handler(request: Request, id: UUID, body: UpdateUserRequest):
    try:
        admin_user = request.state.user
        user = update_user(
            user_id=id,
            organization_id=admin_user.organization_id,
            email=body.email,
            role=body.role,
            is_active=body.is_active
        )
        if user:
            return APIOutput.success(
                data=user.safe_json(),
                message="User updated successfully"
            )
        return APIOutput.failure(
            message="User not found",
            status_code=404
        )
    except ValueError as e:
        return APIOutput.failure(message=str(e), status_code=409)
    except Exception as e:
        return APIOutput.failure(message=str(e), status_code=500)

route = Route(
    function=update_user_handler,
    path="/{id}",
    method="PATCH",
    required_roles=[Role.ADMIN],
    summary="Update a user",
    description="Updates a user's email, role, or activation status by ID within the administrator's organization"
)
