from src.models import APIOutput, Route
from src.logics import delete_organization
from uuid import UUID

async def delete_organization_handler(id: UUID):
    success = delete_organization(id)
    if success:
        return APIOutput.success(
            message="Organization deleted successfully"
        )
    return APIOutput.failure(
        message="Organization not found",
        status_code=404
    )

route = Route(
    function=delete_organization_handler,
    path="/{id}",
    method="DELETE",
    summary="Delete an organization",
    description="Deletes an organization by its UUID"
)
