from pydantic import BaseModel
from src.models import APIOutput, Route, Organization
from src.logics import list_organizations
from typing import List, Optional

class ListOrganizationsRequest(BaseModel):
    # Optional filtering can be added here later
    limit: Optional[int] = None
    offset: Optional[int] = None

async def list_organizations_handler(request: ListOrganizationsRequest):
    try:
        orgs = list_organizations()
        return APIOutput.success(
            data=orgs,
            message="Organizations retrieved successfully"
        )
    except Exception as e:
        return APIOutput.failure(message=str(e), status_code=500)

route = Route(
    function=list_organizations_handler,
    method="POST",
    summary="List all organizations",
    description="Returns a list of all organizations. Requested as POST."
)
