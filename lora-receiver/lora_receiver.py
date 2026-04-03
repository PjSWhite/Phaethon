# Handles:
#   - Initializing the SX1278 (SX127x family) LoRa radio
#   - Listening for incoming packets
#   - Reading raw bytes + RSSI/SNR
#   - CRC validation
#   - Unpacking the binary payload into a Python dict

import struct
import logging
from LoRaRF import SX127x
from config import (
    LORA_BUS, LORA_CS, LORA_RESET, LORA_IRQ,
    LORA_TXEN, LORA_RXEN,
    LORA_FREQUENCY, LORA_BANDWIDTH,
    LORA_SF, LORA_CR, LORA_PREAMBLE_LEN,
)

logger = logging.getLogger(__name__)

PAYLOAD_FORMAT = "<fffffHH"
PAYLOAD_SIZE   = struct.calcsize(PAYLOAD_FORMAT)

PAYLOAD_FIELDS = [
    "temperature",
    "humidity",
    "pressure",
    "pm25",
    "pm10",
    "aqi",
    "device_id",
]

def init_lora() -> SX127x:
    """
    Initialize the SX1278 radio and put it in continuous-receive mode.
    Returns the configured SX127x instance.
    """
    lora = SX127x()

    logger.info("Initializing SX1278 LoRa radio...")
    lora.begin(
        bus=LORA_BUS,
        cs=LORA_CS,
        reset=LORA_RESET,
        irq=LORA_IRQ,
        txen=LORA_TXEN,
        rxen=LORA_RXEN,   
    )

    lora.setFrequency(LORA_FREQUENCY)
    lora.setRxGain(lora.RX_GAIN_BOOSTED)
    lora.setLoRaModulation(
        LORA_SF,
        LORA_BANDWIDTH,
        LORA_CR,
    )
    lora.setLoRaPacket(
        lora.HEADER_EXPLICIT,   
        LORA_PREAMBLE_LEN,
        PAYLOAD_SIZE,           
        crcType=True,           
    )
    lora.setSyncWord(0x34)
    lora.request(lora.RX_CONTINUOUS)
    
    logger.info(
        "SX1278 listening on %.0f MHz  SF%d  BW%d Hz",
        LORA_FREQUENCY / 1e6,
        LORA_SF,
        LORA_BANDWIDTH,
    )
    return lora

def wait_for_packet(lora: SX127x) -> bool:
    """
    Non-blocking check: returns True if a complete packet
    is available in the FIFO buffer, False otherwise.

    Call this in a loop — it does NOT block the thread.
    """
    return lora.available() > 0

def read_packet(lora: SX127x) -> dict | None:
    """
    Read one packet from the radio's FIFO buffer.

    Steps:
      1. Drain raw bytes from the FIFO
      2. Check the IRQ status register for a CRC error flag
      3. Validate the payload length
      4. Unpack binary bytes → named dict fields
      5. Attach RSSI and SNR metadata from the radio

    Returns a populated dict on success, or None if the packet
    should be discarded (CRC failure, wrong length, unpack error).
    """
    # ── Step 1: Read raw bytes from the FIFO ─────────────────
    raw_bytes = bytes([lora.read() for _ in range(lora.available())])

    # ── Step 2: CRC check ────────────────────────────────────
    # On SX127x, after a receive the IRQ register's CRC_ERR bit
    # is set if the hardware detected a checksum mismatch.
    # We check it here before trusting the payload content.
    if lora.getIrqStatus() & lora.IRQ_CRC_ERR:
        logger.warning("CRC error detected — packet discarded")
        lora.clearIrqStatus(lora.IRQ_ALL)
        return None
    
    lora.clearIrqStatus(lora.IRQ_ALL)   # always clear after reading

    # ── Step 3: Length check ──────────────────────────────────
    if len(raw_bytes) != PAYLOAD_SIZE:
        logger.warning(
            "Unexpected payload length: got %d bytes, expected %d — discarded",
            len(raw_bytes),
            PAYLOAD_SIZE,
        )
        return None
    
    # ── Step 4: Unpack binary payload ─────────────────────────
    try:
        values = struct.unpack(PAYLOAD_FORMAT, raw_bytes)
    except struct.error as exc:
        logger.error("struct.unpack failed: %s", exc)
        return None

    data = dict(zip(PAYLOAD_FIELDS, values))

    # ── Step 5: Attach radio signal metadata ──────────────────
    data["rssi"] = lora.packetRssi()    # signal strength in dBm
    data["snr"]  = lora.snr()           # signal-to-noise ratio in dB

    logger.debug("Unpacked packet: %s", data)
    return data
