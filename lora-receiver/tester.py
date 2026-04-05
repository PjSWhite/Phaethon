import random
import time
from redis_manager import connect_redis, publish_to_redis
from logger import setup_logger

logger = setup_logger("redis_test", "receiver_test_redis.log")

def test_redis():
    logger.info("Attempting to start redis tester")

    # Create redis client
    redis_client = connect_redis()

    # Define some aqi words
    aqi_words = ["Good", "Moderate", "Unhealthy", "Very Unhealthy", "Hazardous"]

    try:
        logger.info("Running dummy server")

        # Delay before starting
        time.sleep(1)
        
        while True:
            payload = {
                "temperature": random.randint(1, 100),
                "pressure": random.randint(1, 100),
                "humidity": random.randint(1, 100),
                "pm25": random.randint(1, 100),
                "pm10": random.randint(1, 100),
                "aqi": aqi_words[random.randint(0,4)],
            }

            publish_to_redis(redis_client, payload)
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutdown requested (Ctrl+C). Closing connections...")
    finally:
        redis_client.close()
        logger.info("Test Redis stopped cleanly.")

if __name__ == "__main__":
    test_redis()
