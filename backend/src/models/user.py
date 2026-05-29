from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from .role import Role


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    email: str
    password_hash: str
    role: Role
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    def safe_json(self) -> dict:
        """
        Returns the user details as a dict without the password_hash.
        """
        return self.model_dump(exclude={"password_hash"})
