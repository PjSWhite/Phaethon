# Handles all SQLite operations:
#   - Creating the table on first run
#   - Inserting a new weather reading


import sqlite3
import logging
from config import DB_PATH

logger = logging.getLogger(__name__)

def init_db() -> sqlite3.Connection:
    """
    Open (or create) the SQLite database and ensure the
    weather_readings table exists.

    Returns a live connection object that the caller should
    keep open for the lifetime of the program.
    """
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)

    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weather_readings (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id   INTEGER NOT NULL,
            timestamp   DATETIME DEFAULT (datetime('now','localtime')),
            temperature REAL,        -- °C
            humidity    REAL,        -- % RH
            pressure    REAL,        -- Pa
            pm25        REAL,        -- µg/m³
            pm10        REAL,        -- µg/m³
            aqi         INTEGER,     -- Air Quality Index score
            rssi        INTEGER,     -- Received Signal Strength (dBm)
            snr         REAL         -- Signal-to-Noise Ratio (dB)
        )
    """)
    conn.commit()
    logger.info("SQLite database ready at '%s'", DB_PATH)
    return conn

def insert_reading(conn: sqlite3.Connection, data: dict) -> None:
    """
    Insert one weather reading dictionary into the database.

    Expected keys in `data`:
        device_id, temperature, humidity, pressure,
        pm25, pm10, aqi, rssi, snr
    """
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO weather_readings
            (device_id, temperature, humidity, pressure,
             pm25, pm10, aqi, rssi, snr)
        VALUES
            (:device_id, :temperature, :humidity, :pressure,
             :pm25, :pm10, :aqi, :rssi, :snr)
    """, data)
    conn.commit()
    logger.debug("Inserted reading from device %s into DB", data["device_id"])
