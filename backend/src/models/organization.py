from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime

class Organization(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    name: str
    created_at: datetime
    updated_at: datetime
