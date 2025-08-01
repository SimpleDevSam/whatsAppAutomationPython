from redis.asyncio import Redis
from app.application.settings import get_settings

settings = get_settings()
# single shared Redis client
redis_client: Redis = Redis.from_url(
    settings.redis_url,
    decode_responses=True,
)

async def push_buffer(buffer_key: str, message_data: str) -> int:
    return await redis_client.rpush(buffer_key, message_data)

async def fetch_buffer(buffer_key: str) -> list[str]:
    return await redis_client.lrange(buffer_key, 0, -1)

async def clear_buffer(buffer_key: str) -> int:
    return await redis_client.delete(buffer_key)

# FastAPI dependency
async def get_redis() -> Redis:
    return redis_client