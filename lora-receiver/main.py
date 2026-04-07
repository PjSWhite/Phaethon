# Entry point for the LoRa → SQLite → Redis gateway.


import time
import logger as _logger
from redis_manager import connect_redis, publish_to_redis

from database import init_db, insert_reading
from lora_receiver import init_lora, wait_for_packet, read_packet

logger = _logger.setup_logger()
LOG_FILE = _logger.LOG_FILE

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
