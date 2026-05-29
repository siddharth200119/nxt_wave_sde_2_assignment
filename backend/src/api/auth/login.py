from pydantic import BaseModel, EmailStr
from src.models import APIOutput, Route
from src.logics import login_user
from uuid import UUID

class LoginRequest(BaseModel):
    organization_id: UUID
    email: EmailStr
    password: str

async def login_handler(request: LoginRequest):
    try:
        user, access_token, refresh_token = login_user(
            request.email,
            request.password,
            request.organization_id
        )
        
        if not user:
            return APIOutput.failure(
                message="Invalid email, password, or organization",
                status_code=401
            )
            
        if not user.is_active:
            return APIOutput.failure(
                message="User account is deactivated",
                status_code=403
            )

        return APIOutput.success(
            data={
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": user.safe_json()
            },
            message="Login successful"
        )
    except ValueError as e:
        return APIOutput.failure(
            message=str(e),
            status_code=400
        )
    except Exception as e:
        return APIOutput.failure(message=str(e), status_code=500)

route = Route(
    function=login_handler,
    method="POST",
    summary="User login",
    description="Authenticates a user using email, password, and organization ID"
)
