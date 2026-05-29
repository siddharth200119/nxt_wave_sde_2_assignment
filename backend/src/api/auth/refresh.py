from pydantic import BaseModel
from src.models import APIOutput, Route
from src.logics import rotate_refresh_token

class RefreshRequest(BaseModel):
    refresh_token: str

async def refresh_handler(request: RefreshRequest):
    try:
        user, access_token, refresh_token = rotate_refresh_token(request.refresh_token)
        if not user:
            return APIOutput.failure(
                message="Invalid or expired refresh token",
                status_code=401
            )
            
        return APIOutput.success(
            data={
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": user.safe_json()
            },
            message="Token refreshed successfully"
        )
    except Exception as e:
        return APIOutput.failure(message=str(e), status_code=500)

route = Route(
    function=refresh_handler,
    method="POST",
    summary="Refresh access token",
    description="Exchanges an active refresh token for a new access token and a rotated refresh token."
)
