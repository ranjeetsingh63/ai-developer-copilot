import logging
import sys

from pythonjsonlogger.json import JsonFormatter


def configure_logging() -> None:
    formatter = JsonFormatter(
        "{levelname}{asctime}{name}{message}",
        style="{",
        rename_fields={"levelname": "level", "asctime": "timestamp", "name": "logger"},
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(logging.INFO)

    # Route Uvicorn's own loggers through the same JSON formatter
    for uvicorn_logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        uvicorn_logger = logging.getLogger(uvicorn_logger_name)
        uvicorn_logger.handlers = [handler]
        uvicorn_logger.propagate = False