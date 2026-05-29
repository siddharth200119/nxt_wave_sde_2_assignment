from fastapi import Request, HTTPException, status
from src.models import Role, User


class RoleChecker:
    """
    A FastAPI dependency validator that checks if the authenticated user
    (expected to be attached to request.state.user by an upstream middleware)
    possesses the required roles.
    """

    def __init__(self, allowed_roles: list[Role]):
        self.allowed_roles = allowed_roles

    async def __call__(self, request: Request):
        # 1. Expect authenticated user from request state (set by upstream auth middleware)
        user = getattr(request.state, "user", None)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "status": 401,
                    "code": "UNAUTHORIZED",
                    "message": "User is not authenticated",
                },
            )

        # Ensure the user is a User pydantic instance, or parse if dictionary
        if isinstance(user, dict):
            try:
                user = User(**user)
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={
                        "status": 401,
                        "code": "UNAUTHORIZED",
                        "message": "Invalid user data format in request state",
                    },
                )

        # 2. Check roles
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "status": 403,
                    "code": "FORBIDDEN",
                    "message": f"Role '{user.role.value}' does not have permission to access this resource",
                },
            )

        return user
