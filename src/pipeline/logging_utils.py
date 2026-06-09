import json
import logging
import os
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any


RUN_ID_CTX: ContextVar[int | None] = ContextVar("run_id", default=None)
FILE_PATH_CTX: ContextVar[str | None] = ContextVar("file_path", default=None)
FILE_CHECKSUM_CTX: ContextVar[str | None] = ContextVar("file_checksum", default=None)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        run_id = RUN_ID_CTX.get()
        file_path = FILE_PATH_CTX.get()
        file_checksum = FILE_CHECKSUM_CTX.get()
        if run_id is not None:
            payload["run_id"] = run_id
        if file_path is not None:
            payload["file_path"] = file_path
        if file_checksum is not None:
            payload["file_checksum"] = file_checksum

        known_keys = {
            "name",
            "msg",
            "args",
            "levelname",
            "levelno",
            "pathname",
            "filename",
            "module",
            "exc_info",
            "exc_text",
            "stack_info",
            "lineno",
            "funcName",
            "created",
            "msecs",
            "relativeCreated",
            "thread",
            "threadName",
            "processName",
            "process",
            "message",
            "asctime",
        }
        for key, value in record.__dict__.items():
            if key in known_keys or key.startswith("_"):
                continue
            payload[key] = value

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, default=str)


def configure_logging(log_file_path: str | None = None) -> None:
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    log_format = os.getenv("LOG_FORMAT", "json").lower()
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers.clear()

    if log_format == "json":
        formatter: logging.Formatter = JsonFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s %(levelname)s [%(name)s] %(message)s"
        )

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    root_logger.addHandler(stream_handler)

    if log_file_path:
        file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)


def set_log_context(
    run_id: int | None = None,
    file_path: str | None = None,
    file_checksum: str | None = None,
) -> None:
    RUN_ID_CTX.set(run_id)
    FILE_PATH_CTX.set(file_path)
    FILE_CHECKSUM_CTX.set(file_checksum)


def clear_log_context() -> None:
    RUN_ID_CTX.set(None)
    FILE_PATH_CTX.set(None)
    FILE_CHECKSUM_CTX.set(None)
