import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from contextvars import ContextVar
from logging.handlers import RotatingFileHandler

# Contexto por-request (correlação)
request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)

def set_request_id(request_id: str | None) -> None:
    request_id_ctx.set(request_id)

def get_request_id() -> str | None:
    return request_id_ctx.get()

class ContextFilter(logging.Filter):
    """Injeta request_id automaticamente em todo log record."""
    def filter(self, record: logging.LogRecord) -> bool:
        rid = get_request_id()
        record.request_id = rid
        return True

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }

        # inclui request_id se existir
        rid = getattr(record, "request_id", None)
        if rid:
            payload["request_id"] = rid

        # adiciona extras customizados (extra={...})
        skip = {
            "name", "msg", "args", "levelname", "levelno", "pathname", "filename",
            "module", "exc_info", "exc_text", "stack_info", "lineno", "funcName",
            "created", "msecs", "relativeCreated", "thread", "threadName",
            "processName", "process", "request_id",
        }
        for k, v in record.__dict__.items():
            if k.startswith("_") or k in skip:
                continue
            payload[k] = v

        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=False)

def _rotating_file_handler(path: Path, formatter: logging.Formatter, level: int) -> RotatingFileHandler:
    path.parent.mkdir(parents=True, exist_ok=True)
    h = RotatingFileHandler(
        path,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8",
    )
    h.setLevel(level)
    h.setFormatter(formatter)
    h.addFilter(ContextFilter())
    return h

def setup_logging() -> None:
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    log_dir = Path(os.getenv("LOG_DIR", "logs"))
    formatter = JsonFormatter()

    # Console (stdout)
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(level)
    console.setFormatter(formatter)
    console.addFilter(ContextFilter())

    # Arquivos separados
    http_file = _rotating_file_handler(log_dir / "http.log", formatter, level)
    moderation_file = _rotating_file_handler(log_dir / "moderation.log", formatter, level)

    # Root logger (tudo que não for específico vai pro console)
    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(level)
    root.addHandler(console)

    # Logger HTTP (somente http.log + console)
    http_logger = logging.getLogger("multimodal_moderation.http")
    http_logger.handlers.clear()
    http_logger.setLevel(level)
    http_logger.addHandler(http_file)
    http_logger.addHandler(console)
    http_logger.propagate = False  # evita duplicar no root

    # Logger Moderation (somente moderation.log + console)
    mod_logger = logging.getLogger("multimodal_moderation.moderation")
    mod_logger.handlers.clear()
    mod_logger.setLevel(level)
    mod_logger.addHandler(moderation_file)
    mod_logger.addHandler(console)
    mod_logger.propagate = False  # evita duplicar no root

    # reduzir barulho de libs
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
