import redis
import json
from config import REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_TOPIC
from logger import getLogger

logger = getLogger()

def connect_redis() -> redis.Redis:
    """
    Create and verify a connection to the Redis server.
    Raises redis.ConnectionError if the server is unreachable.
    """
    client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        decode_responses=True,
    )
    client.ping()
    logger.info(
        "Connected to Redis at %s:%d (db=%d)",
        REDIS_HOST, REDIS_PORT, REDIS_DB
    )
    return client


def publish_to_redis(client: redis.Redis, data: dict) -> None:
    """
    Serialize `data` to JSON and publish it on the
    configured Redis topic (channel).
    """
    payload_json = json.dumps(data)
    receivers = client.publish(REDIS_TOPIC, payload_json)
    logger.info(
        "Published to Redis channel '%s' → %d subscriber(s) received it",
        REDIS_TOPIC,
        receivers,
    )

