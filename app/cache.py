
import json
import os
import redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)


def get_cached_json(key: str):
    """Retrieve and parse cached JSON data."""
    try:
        data = redis_client.get(key)
        return json.loads(data) if data else None
    except Exception:
        return None 


def set_cached_json(key: str, data: dict, expire_seconds: int = 3600):
    """Store data in Redis as JSON with an expiration time (default: 1 hour)."""
    try:
        redis_client.setex(key, expire_seconds, json.dumps(data))
    except Exception:
        pass
