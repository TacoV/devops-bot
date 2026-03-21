import logging
import os
from rich.logging import RichHandler

_LOGGER_INITIALIZED = False

def get_logger(name: str = "devops-bot") -> logging.Logger:
    global _LOGGER_INITIALIZED

    logger = logging.getLogger(name)

    if _LOGGER_INITIALIZED:
        return logger

    level = os.getenv("LOG_LEVEL", "INFO").upper()

    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[
            RichHandler(
                rich_tracebacks=True,
                show_time=True,
                show_path=False
            )
        ],
    )

    _LOGGER_INITIALIZED = True
    return logger