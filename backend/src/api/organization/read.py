from src.models import APIOutput, Route, Role
from src.logics import read_organization
from uuid import UUID

async def read_organization_handler(id: UUID):
    try:
        org = read_organization(id)
        if org:
            return APIOutput.success(
                data=org,
                message="Organization retrieved successfully"
            )
        return APIOutput.failure(
            message="Organization not found",
            status_code=404
        )
    except Exception as e:
        return APIOutput.failure(message=str(e), status_code=500)

route = Route(
    function=read_organization_handler,
    path="/{id}",
    method="GET",
    required_roles=[Role.ADMIN],
    summary="Get an organization by ID",
    description="Returns an organization's details based on its UUID"
)
