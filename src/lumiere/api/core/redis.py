import redis.asyncio as redis
from lumiere.api.core.config import api_settings

class RedisClient:
    def __init__(self):
        self.pool = None

    async def connect(self):
        self.pool = redis.from_url(
            api_settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
        await self.pool.ping()
        print("Successfully connected to Redis cache.")

    async def disconnect(self):
        if self.pool:
            await self.pool.close()
            print("Redis connection closed.")

redis_client = RedisClient()