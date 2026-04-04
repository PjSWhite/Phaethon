# Entry point for the LoRa → SQLite → Redis gateway.


import json
import time
import logging
import redis

from config import REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_TOPIC
from database import init_db, insert_reading
from lora_receiver import init_lora, wait_for_packet, read_packet


LOG_FORMAT    = "%(asctime)s  [%(levelname)s]  %(name)s — %(message)s"
LOG_DATEFMT   = "%Y-%m-%d %H:%M:%S"
LOG_FILE      = "receiver.log"

formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=LOG_DATEFMT)

# Handler 1 — stdout
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

# Handler 2 — log file
file_handler = logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8")
file_handler.setFormatter(formatter)

logging.basicConfig(level=logging.INFO, handlers=[stream_handler, file_handler])

logger = logging.getLogger("main")


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

#Herobrine be like: Chicken Jockey
def main() -> None:
    logger.info("=== LoRa → Redis Weather Gateway starting ===")
    logger.info("Logging to stdout and '%s'", LOG_FILE)

    db_conn      = init_db()
    redis_client = connect_redis()
    lora         = init_lora()

    logger.info("All systems ready. Waiting for LoRa packets...\n")

    try:
        while True:
            if not wait_for_packet(lora):
                time.sleep(0.05)
                continue

            data = read_packet(lora)
            if data is None:
                continue

            logger.info(
                "Packet from device #%d | "
                "Temp=%.1f°C  Hum=%.1f%%  Press=%.1fhPa  "
                "PM2.5=%.1f  PM10=%.1f  AQI=%d | "
                "RSSI=%d dBm  SNR=%.1f dB",
                data["device_id"],
                data["temperature"],
                data["humidity"],
                data["pressure"],
                data["pm25"],
                data["pm10"],
                data["aqi"],
                data["rssi"],
                data["snr"],
            )

            insert_reading(db_conn, data)
            publish_to_redis(redis_client, data)

    except KeyboardInterrupt:
        logger.info("Shutdown requested (Ctrl+C). Closing connections...")
    finally:
        db_conn.close()
        redis_client.close()
        logger.info("Gateway stopped cleanly.")


if __name__ == "__main__":
    main()