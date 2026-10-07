import redis
from app.core.config import settings

sync_redis = redis.from_url(settings.redis_url, decode_responses=True)
