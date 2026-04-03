# Entry point for the LoRa → SQLite → Redis gateway.
#
# Flow:
#   1. Initialize LoRa radio, SQLite DB, and Redis connection
#   2. Loop forever:
#       a. Wait for an incoming LoRa packet
#       b. Read and unpack the packet
#       c. Insert the data into SQLite
#       d. Publish the data to the Redis "weather" channel

import json
import logging
import time
import redis

from config import REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_TOPIC
from database import init_db, insert_reading
from lora_receiver import init_lora, wait_for_packet, read_packet

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(levelname)s]  %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
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
        decode_responses=True,   # return str instead of bytes
    )
    client.ping()   # will raise if Redis is not running
    logger.info(
        "Connected to Redis at %s:%d (db=%d)",
        REDIS_HOST, REDIS_PORT, REDIS_DB
    )
    return client

def publish_to_redis(client: redis.Redis, data: dict) -> None:
    """
    Serialize `data` to JSON and publish it on the
    configured Redis topic (channel).

    Any subscriber listening on the "weather" channel will
    instantly receive this message.
    """
    payload_json = json.dumps(data)
    receivers = client.publish(REDIS_TOPIC, payload_json)
    logger.info(
        "Published to Redis channel '%s' → %d subscriber(s) received it",
        REDIS_TOPIC,
        receivers,
    )

def main() -> None:
    # ── Phase 1: Initialization ───────────────────────────────
    logger.info("=== LoRa → Redis Weather Gateway starting ===")

    db_conn     = init_db()
    redis_client = connect_redis()
    lora        = init_lora()

    logger.info("All systems ready. Waiting for LoRa packets...\n")

    # ── Phase 2: Main Loop ────────────────────────────────────
    try:
        while True:
            # (a) Wait — poll until a packet arrives
            if not wait_for_packet(lora):
                time.sleep(0.05)    # 50 ms idle sleep; keeps CPU usage low
                continue

            # (b) Read and unpack the packet
            data = read_packet(lora)
            if data is None:
                # read_packet already logged the reason (CRC error, etc.)
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

            # (c) Persist to SQLite
            insert_reading(db_conn, data)

            # (d) Publish to Redis on the "weather" topic
            publish_to_redis(redis_client, data)

    except KeyboardInterrupt:
        logger.info("Shutdown requested (Ctrl+C). Closing connections...")
    finally:
        db_conn.close()
        redis_client.close()
        logger.info("Gateway stopped cleanly.")

if __name__ == "__main__":
    main()