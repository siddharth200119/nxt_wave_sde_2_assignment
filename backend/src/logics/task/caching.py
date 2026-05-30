from uuid import UUID
from src.utils.redis import get_redis
from src.utils import logger


async def invalidate_task_cache(organization_id: UUID):
    """
    Scans and invalidates all Redis cache keys prefixed with tasks:org:{organization_id}:*
    to ensure listing queries always present the latest state.
    """
    try:
        redis_client = await get_redis()
        # Redis scan for matching keys
        pattern = f"tasks:org:{organization_id}:*"
        keys = []
        async for key in redis_client.scan_iter(match=pattern):
            keys.append(key)
            
        if keys:
            await redis_client.delete(*keys)
            logger.info(f"⚡ Invalidated {len(keys)} task cache keys matching pattern: {pattern}")
        else:
            logger.debug(f"⚡ No task cache keys matching pattern: {pattern}")
    except Exception as e:
        logger.error(f"⚡ Failed to invalidate task cache: {e}")
            
