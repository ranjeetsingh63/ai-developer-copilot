import logging
import sys
from pythonjsonlogger import jsonlogger


def setup_logging() -> None:
    """Configures structured JSON logging for the application."""
    logger = logging.getLogger()

    # Clear existing handlers to prevent duplicate logs (useful during hot-reloads)
    if logger.hasHandlers():
        logger.handlers.clear()

    logger.setLevel(logging.INFO)

    # Output logs to standard output (which Docker captures perfectly)
    log_handler = logging.StreamHandler(sys.stdout)

    # Define the structure of our JSON logs
    formatter = jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
        rename_fields={
            "levelname": "level",
            "asctime": "timestamp"
        }
    )

    log_handler.setFormatter(formatter)
    logger.addHandler(log_handler)

    # Suppress default Uvicorn access logs since we will handle request logging via middleware
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
