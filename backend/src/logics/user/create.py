from src.utils.database import get_db_cursor
from src.utils.hasher import hash_string
from src.models.user import User
from src.models.role import Role
from src.logics.user.get_by_email import get_user_by_email
from uuid import uuid4, UUID

def create_user(organization_id: UUID, email: str, password: str, role: Role) -> User:
    """
    Creates a new user under the specified organization.
    Checks email uniqueness within the organization first.
    """
    existing_user = get_user_by_email(email, organization_id)
    if existing_user:
        raise ValueError("User with this email already exists in the organization")

    password_hash = hash_string(password)
    user_id = uuid4()
    
    with get_db_cursor() as cursor:
        cursor.execute(
            "INSERT INTO users (id, organization_id, email, password_hash, role) "
            "VALUES (%s, %s, %s, %s, %s) RETURNING *",
            (user_id, organization_id, email, password_hash, role.value)
        )
        result = cursor.fetchone()
        return User.model_validate(result)
