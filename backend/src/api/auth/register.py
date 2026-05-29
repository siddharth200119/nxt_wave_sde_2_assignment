from pydantic import BaseModel, EmailStr
from src.models import APIOutput, Route, Role
from src.logics import register_user
from uuid import UUID

class RegisterRequest(BaseModel):
    organization_id: UUID
    email: EmailStr
    password: str
    role: Role = Role.MEMBER

async def register_handler(request: RegisterRequest):
    try:
        user, access_token, refresh_token = register_user(
            request.organization_id,
            request.email,
            request.password,
            request.role
        )
        
        return APIOutput.success(
            data={
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": user.safe_json()
            },
            message="User registered successfully",
            status_code=201
        )
    except ValueError as e:
        status_code = 400 if "Organization" in str(e) else 409
        return APIOutput.failure(
            message=str(e),
            status_code=status_code
        )
    except Exception as e:
        return APIOutput.failure(message=str(e), status_code=500)

route = Route(
    function=register_handler,
    method="POST",
    summary="Register a new user",
    description="Creates a new user account within an organization"
)
