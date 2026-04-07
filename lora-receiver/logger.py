import logging

DEFAULT_NAME = 'main'
LOG_FORMAT    = "%(asctime)s  [%(levelname)s]  %(name)s — %(message)s"
LOG_DATEFMT   = "%Y-%m-%d %H:%M:%S"
LOG_FILE      = "receiver.log"

_init_name = ""

def setup_logger(name: str = DEFAULT_NAME, file=LOG_FILE) -> logging.Logger:
    global _init_name
    formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=LOG_DATEFMT)

    # Handler 1 — stdout
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    # Handler 2 — log file
    file_handler = logging.FileHandler(file, mode="a", encoding="utf-8")
    file_handler.setFormatter(formatter)

    logging.basicConfig(level=logging.INFO, handlers=[stream_handler, file_handler])

    logger = logging.getLogger(name)
    _init_name = name

    return logger

def getLogger():
    return logging.getLogger(_init_name)
