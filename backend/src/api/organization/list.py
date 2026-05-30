from src.models import APIOutput, Route, Role
from src.logics import list_organizations
from typing import Optional

async def list_organizations_handler(limit: Optional[int] = None, offset: Optional[int] = None):
    try:
        orgs = list_organizations()
        
        # Apply standard pagination limit/offset slicing in-memory
        if limit is not None or offset is not None:
            start = offset or 0
            end = start + limit if limit is not None else len(orgs)
            orgs = orgs[start:end]
            
        return APIOutput.success(
            data=orgs,
            message="Organizations retrieved successfully"
        )
    except Exception as e:
        return APIOutput.failure(message=str(e), status_code=500)

route = Route(
    function=list_organizations_handler,
    method="GET",
    required_roles=[],
    summary="List all organizations",
    description="Returns a list of all organizations. Requested as GET."
)
