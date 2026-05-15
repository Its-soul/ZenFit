from redis import Redis

from app.config import settings


def get_redis_client() -> Redis:
    return Redis.from_url(settings.redis_url, decode_responses=True)


def redis_health() -> bool:
    client = get_redis_client()
    return bool(client.ping())

