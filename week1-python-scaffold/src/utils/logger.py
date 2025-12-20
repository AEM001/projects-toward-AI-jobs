
import logging

from config import settings


def get_logger(name: str | None = None) -> logging.Logger:
    if name is None:
        name = settings.APP_NAME
    return logging.getLogger(name)
