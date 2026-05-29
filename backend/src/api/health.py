from src.models import APIOutput, Route
from src.logics.health import get_server_stats


async def health():
    try:
        stats = await get_server_stats()
        return APIOutput.success(
            status_code=200, message="server is healthy", data=stats
        )
    except Exception as e:
        return APIOutput.failure(message=str(e), status_code=500)


route = Route(
    function=health,
    method="GET",
    summary="Get server health status",
    description="Returns CPU, RAM, Disk, Database and Redis health information"
)
