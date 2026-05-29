import os
import json
import asyncio
from typing import Dict, Optional, Any
from redis.asyncio import Redis
from src.utils import logger
import time

# -------------------------
# Config
# -------------------------

def get_redis_config():
    return {
        "host": os.getenv("REDIS_HOST", "localhost"),
        "port": int(os.getenv("REDIS_PORT", 6379)),
        "db": int(os.getenv("REDIS_DB", 0)),
        "decode_responses": True,
    }


# -------------------------
# Client singleton
# -------------------------

_redis: Redis | None = None


async def get_redis() -> Redis:
    global _redis

    if _redis is None:
        cfg = get_redis_config()
        logger.info(f"Connecting to Redis {cfg['host']}:{cfg['port']}/{cfg['db']}")

        _redis = Redis(**cfg)

        # Health check
        await _redis.ping()
        logger.info("Redis connection established")

    return _redis


async def check_redis_health():
    """Check Redis connection status and measure latency"""
    start_time = time.perf_counter()
    try:
        client = await get_redis()
        await client.ping()
        latency_ms = (time.perf_counter() - start_time) * 1000
        return {
            "status": "connected",
            "latency_ms": round(latency_ms, 2)
        }
    except Exception as e:
        latency_ms = (time.perf_counter() - start_time) * 1000
        return {
            "status": "failed",
            "error": str(e),
            "latency_ms": round(latency_ms, 2)
        }