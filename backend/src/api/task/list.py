from fastapi import Request, Query
from src.models import APIOutput, Route, Role, TaskStatus, TaskPriority
from src.logics import list_tasks
from src.utils.redis import get_redis
from uuid import UUID
from typing import Optional
import json


async def list_tasks_handler(
    request: Request,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    status: Optional[TaskStatus] = Query(None, description="Filter by task status"),
    priority: Optional[TaskPriority] = Query(None, description="Filter by task priority"),
    assignee_id: Optional[UUID] = Query(None, description="Filter by assignee user ID")
):
    try:
        user = request.state.user
        
        # Enforce security model: MEMBERS can only list tasks assigned to them
        if user.role == Role.MEMBER:
            assignee_id = user.id

        # 1. Generate caching keys
        cache_key = (
            f"tasks:org:{user.organization_id}:"
            f"page:{page}:limit:{limit}:"
            f"status:{status.value if status else 'all'}:"
            f"priority:{priority.value if priority else 'all'}:"
            f"assignee:{assignee_id if assignee_id else 'all'}"
        )
        
        # 2. Try cache hit
        redis_client = None
        try:
            redis_client = await get_redis()
            cached_data = await redis_client.get(cache_key)
            if cached_data:
                parsed_cache = json.loads(cached_data)
                return APIOutput.success(
                    data=parsed_cache["data"],
                    message="Tasks retrieved successfully (cached)"
                )
        except Exception as e:
            # Redis failure should not crash the API request, fallback to database gracefully
            pass

        # 3. Call database logics
        result = list_tasks(
            organization_id=user.organization_id,
            status=status,
            priority=priority,
            assignee_id=assignee_id,
            page=page,
            limit=limit
        )

        # 4. Serialize tasks using safe_json() to scrub password_hash fields
        safe_tasks = [t.safe_json() for t in result["tasks"]]
        response_data = {
            "tasks": safe_tasks,
            "pagination": result["pagination"]
        }

        # 5. Populate cache
        if redis_client:
            try:
                # Cache with 300 seconds (5 minutes) TTL
                await redis_client.setex(
                    cache_key,
                    300,
                    json.dumps({"data": response_data})
                )
            except Exception as e:
                pass

        return APIOutput.success(
            data=response_data,
            message="Tasks retrieved successfully"
        )
    except Exception as e:
        return APIOutput.failure(message=str(e), status_code=500)


route = Route(
    function=list_tasks_handler,
    method="GET",
    required_roles=[Role.ADMIN, Role.MANAGER, Role.MEMBER],
    summary="List all tasks",
    description="Returns a paginated and filtered list of tasks within the user's organization"
)
