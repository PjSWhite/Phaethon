# Central configuration for the LoRa Receiver Gateway.
# Adjust these values to match your hardware and environment.
# ─────────────────────────────────────────────────────────────

# ── LoRa Radio Settings ──────────────────────────────────────
# SPI bus and chip-select for your LoRa module (Raspberry Pi SPI0)

LORA_BUS          = 0
LORA_CS           = 0
LORA_RESET        = 22
LORA_IRQ          = 16

LORA_TXEN         = -1
LORA_RXEN         = -1

LORA_FREQUENCY    = 433E6
LORA_BANDWIDTH    = 125000
LORA_SF           = 7
LORA_CR           = 5
LORA_PREAMBLE_LEN = 8

DB_PATH = "weather_data.db"

REDIS_HOST   = "localhost"
REDIS_PORT   = 6379
REDIS_DB     = 0
REDIS_TOPIC  = "weather"