from redis import Redis

from core.config import redis_url

redis_client = Redis.from_url(redis_url(), decode_responses=True)
