from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional
from .task_priority import TaskPriority
from .task_status import TaskStatus
from .user import User
from .organization import Organization


class Task(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    title: str
    description: Optional[str] = None
    priority: TaskPriority
    status: TaskStatus
    assignee_id: Optional[UUID] = None
    due_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    # Hydrated models (relations)
    organization: Optional[Organization] = None
    assigned_to: Optional[User] = None

    def safe_json(self) -> dict:
        """
        Returns the task details as a JSON-serializable dict, sanitizing nested user objects of password hashes.
        """
        data = self.model_dump(mode="json")
        if data.get("assigned_to"):
            data["assigned_to"].pop("password_hash", None)
        return data
