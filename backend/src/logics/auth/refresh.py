from datetime import datetime, timezone
from src.utils.database import get_db_cursor
from src.utils.hasher import hash_string
from src.models.user import User
from src.utils.auth import create_access_token, create_refresh_token
from typing import Tuple, Optional

def rotate_refresh_token(refresh_token: str) -> Tuple[Optional[User], Optional[str], Optional[str]]:
    """
    Validates a refresh token, ensures it is not expired,
    deletes it from the database (rotation policy), and returns (User, access_token, refresh_token).
    """
    token_hash = hash_string(refresh_token)
    now = datetime.now(timezone.utc)

    with get_db_cursor() as cursor:
        # Find token and join with users to verify it is valid and user is active
        cursor.execute(
            "SELECT u.*, rt.expires_at FROM refresh_tokens rt "
            "JOIN users u ON rt.user_id = u.id "
            "WHERE rt.token_hash = %s AND u.is_active = true",
            (token_hash,)
        )
        result = cursor.fetchone()
        if not result:
            return None, None, None

        # Verify expiration
        expires_at = result["expires_at"]
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
            
        if expires_at < now:
            # Token is expired, delete it from the DB to clean up
            cursor.execute("DELETE FROM refresh_tokens WHERE token_hash = %s", (token_hash,))
            return None, None, None

        # Revoke the used token immediately (rotation policy)
        cursor.execute("DELETE FROM refresh_tokens WHERE token_hash = %s", (token_hash,))

        # Extract user
        user = User.model_validate(result)

        # Generate new tokens
        access_token = create_access_token(user.id, user.organization_id, user.role)
        new_refresh_token = create_refresh_token(user.id)

        return user, access_token, new_refresh_token
