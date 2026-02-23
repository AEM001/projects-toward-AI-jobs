
import logging
import logging.config

from config import settings


def setup_logging() -> None:
    settings.LOG_DIR.mkdir(parents=True, exist_ok=True)

    handlers = {
        "file": {
            "class": "logging.FileHandler",
            "level": settings.LOG_LEVEL,
            "formatter": "standard",
            "filename": str(settings.LOG_FILE),
            "encoding": "utf-8",
        }
    }
    root_handlers = ["file"]

    if settings.LOG_TO_CONSOLE:
        handlers["console"] = {
            "class": "logging.StreamHandler",
            "level": settings.LOG_LEVEL,
            "formatter": "standard",
        }
        root_handlers.append("console")

    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s %(levelname)s [%(name)s] %(message)s",
            }
        },
        "handlers": handlers,
        "root": {
            "level": settings.LOG_LEVEL,
            "handlers": root_handlers,
        },
    }

    logging.config.dictConfig(config)
