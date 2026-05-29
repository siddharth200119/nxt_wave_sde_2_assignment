from src.utils.database import get_db_cursor
from src.models.user import User
from src.models.role import Role
from uuid import UUID
from typing import Optional
from datetime import datetime, timezone

def update_user(
    user_id: UUID, 
    organization_id: UUID, 
    email: Optional[str] = None, 
    role: Optional[Role] = None, 
    is_active: Optional[bool] = None
) -> Optional[User]:
    """
    Updates the email, role, and/or is_active status of a user belonging to the organization.
    Only provided (non-None) fields will be updated.
    """
    # Verify the user exists in this organization
    with get_db_cursor() as cursor:
        cursor.execute(
            "SELECT * FROM users WHERE id = %s AND organization_id = %s",
            (user_id, organization_id)
        )
        existing_user = cursor.fetchone()
        if not existing_user:
            return None

        # Check if email is being updated and conflicts with another user
        if email is not None and email != existing_user["email"]:
            cursor.execute(
                "SELECT 1 FROM users WHERE email = %s AND organization_id = %s AND id != %s",
                (email, organization_id, user_id)
            )
            if cursor.fetchone():
                raise ValueError("Another user with this email already exists in the organization")

        # Build dynamic update query
        update_fields = []
        params = []
        
        if email is not None:
            update_fields.append("email = %s")
            params.append(email)
        if role is not None:
            update_fields.append("role = %s")
            params.append(role.value)
        if is_active is not None:
            update_fields.append("is_active = %s")
            params.append(is_active)
            
        if not update_fields:
            # Nothing to update, return the current user
            return User.model_validate(existing_user)

        update_fields.append("updated_at = %s")
        params.append(datetime.now(timezone.utc))

        params.extend([user_id, organization_id])
        query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = %s AND organization_id = %s RETURNING *"
        
        cursor.execute(query, params)
        result = cursor.fetchone()
        if result:
            return User.model_validate(result)
        return None
