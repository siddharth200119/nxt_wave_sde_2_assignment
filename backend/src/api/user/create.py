from fastapi import Request
from pydantic import BaseModel, EmailStr
from src.models import APIOutput, Route, Role
from src.logics import create_user

class CreateUserRequest(BaseModel):
    email: EmailStr
    password: str
    role: Role = Role.MEMBER

async def create_user_handler(request: Request, body: CreateUserRequest):
    try:
        admin_user = request.state.user
        user = create_user(
            organization_id=admin_user.organization_id,
            email=body.email,
            password=body.password,
            role=body.role
        )
        return APIOutput.success(
            data=user.safe_json(),
            message="User created successfully",
            status_code=201
        )
    except ValueError as e:
        return APIOutput.failure(message=str(e), status_code=409)
    except Exception as e:
        return APIOutput.failure(message=str(e), status_code=500)

route = Route(
    function=create_user_handler,
    path="/",
    method="POST",
    required_roles=[Role.ADMIN],
    summary="Create a new user",
    description="Creates a new user account within the administrator's organization"
)
