from pydantic import BaseModel
from src.models import APIOutput, Route, Organization
from src.logics import create_organization

class CreateOrganizationRequest(BaseModel):
    name: str

async def create_organization_handler(request: CreateOrganizationRequest):
    org = create_organization(request.name)
    return APIOutput.success(
        data=org,
        message="Organization created successfully",
        status_code=201
    )

route = Route(
    function=create_organization_handler,
    path='/',
    method="POST",
    summary="Create a new organization",
    description="Creates a new organization with the provided name"
)
