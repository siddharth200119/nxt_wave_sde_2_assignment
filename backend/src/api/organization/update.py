from pydantic import BaseModel
from src.models import APIOutput, Route, Role
from src.logics import update_organization
from uuid import UUID

class UpdateOrganizationRequest(BaseModel):
    name: str

async def update_organization_handler(id: UUID, request: UpdateOrganizationRequest):
    try:
        org = update_organization(id, request.name)
        if org:
            return APIOutput.success(
                data=org,
                message="Organization updated successfully"
            )
        return APIOutput.failure(
            message="Organization not found",
            status_code=404
        )
    except Exception as e:
        return APIOutput.failure(message=str(e), status_code=500)

route = Route(
    function=update_organization_handler,
    path="/{id}",
    method="PATCH",
    required_roles=[Role.ADMIN],
    summary="Update an organization",
    description="Updates an organization's name by its UUID"
)
