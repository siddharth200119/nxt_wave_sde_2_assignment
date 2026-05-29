import asyncio
from fastapi import Request
from src.models import SSEOutput, Route
from src.logics.health import get_server_stats


async def health_generator():
    while True:
        stats = await get_server_stats()
        yield stats
        await asyncio.sleep(10)


async def health(request: Request):
    return SSEOutput.stream(request=request, generator=health_generator())


route = Route(
    function=health,
    method="GET",
    summary="Stream server health status",
    description="Streams CPU, RAM, Disk, Database and Redis health information every 10 seconds"
)