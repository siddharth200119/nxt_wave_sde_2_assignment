from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from src.utils.auth import verify_access_token
from src.utils.database import get_db_cursor
from src.models import User
from uuid import UUID


class AuthenticationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        
        # 1. Skip auth checks for public routes
        PUBLIC_PATHS = {
            "/api/auth/login",
            "/api/auth/register",
            "/api/auth/refresh",
            "/api/health",
            "/docs",
            "/redoc",
            "/openapi.json"
        }
        
        # Also allow preflight (OPTIONS) requests
        if path in PUBLIC_PATHS or request.method == "OPTIONS":
            return await call_next(request)

        # 2. Extract Bearer token
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JSONResponse(
                status_code=401,
                content={
                    "status": 401,
                    "code": "UNAUTHORIZED",
                    "message": "Authorization header is missing"
                }
            )

        if not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={
                    "status": 401,
                    "code": "UNAUTHORIZED",
                    "message": "Authorization header must be Bearer <token>"
                }
            )

        token = auth_header.split(" ")[1]

        # 3. Decode & Verify Access Token
        try:
            payload = verify_access_token(token)
        except Exception as exc:
            # If verify_access_token raises HTTPException, it contains detail dict
            detail = getattr(exc, "detail", None)
            if not isinstance(detail, dict):
                detail = {
                    "status": 401,
                    "code": "UNAUTHORIZED",
                    "message": str(exc)
                }
            return JSONResponse(
                status_code=401,
                content=detail
            )

        user_id = payload.get("sub")
        if not user_id:
            return JSONResponse(
                status_code=401,
                content={
                    "status": 401,
                    "code": "UNAUTHORIZED",
                    "message": "Invalid token payload: missing sub claim"
                }
            )

        # 4. Fetch Active User from Database
        try:
            user_uuid = UUID(user_id)
            with get_db_cursor(commit=False) as cursor:
                cursor.execute("SELECT * FROM users WHERE id = %s", (user_uuid,))
                user_record = cursor.fetchone()

            if not user_record:
                return JSONResponse(
                    status_code=401,
                    content={
                        "status": 401,
                        "code": "UNAUTHORIZED",
                        "message": "User account not found"
                    }
                )

            user = User.model_validate(user_record)
            if not user.is_active:
                return JSONResponse(
                    status_code=403,
                    content={
                        "status": 403,
                        "code": "FORBIDDEN",
                        "message": "User account is deactivated"
                    }
                )

            # 5. Populate request state user
            request.state.user = user
        except Exception as exc:
            return JSONResponse(
                status_code=500,
                content={
                    "status": 500,
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": f"Authentication database error: {exc}"
                }
            )

        return await call_next(request)
