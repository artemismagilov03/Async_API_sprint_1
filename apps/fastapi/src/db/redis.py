from typing import Optional
from redis.asyncio import Redis

rd: Optional[Redis] = None


async def get_redis() -> Redis:
    return rd
