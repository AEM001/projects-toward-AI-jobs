import logging
import sys
from pathlib import Path
from typing import Optional

def get_log_formatter()->logging.Formatter:
    return logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

def get_console_handler() -> logging.Handler:
    handler=logging.StreamHandler(sys.stdout)
    handler.setFormatter(get_log_formatter())
    handler.setLevel(logging.DEBUG)
    return handler
    
def get_file_handler(log_file :str="app.log")->logging.Handler:
    handler = logging.FileHandler(log_file)
    handler.setFormatter(get_log_formatter())
    handler.setLevel(logging.DEBUG)
    return handler

def setup_logging(
    level:str="INFO",log_to_file:bool=False,log_file:str="app.log")->logging.Logger:

    numeric_level=getattr(logging,level.upper(),logging.INFO)#confused
# set root logger
    logger=logging.getLogger("fastapi_todo")
    logger.setLevel(numeric_level)

    logger.handlers.clear()

    console_handler=get_console_handler()
    logger.addHandler(console_handler)
    # optional file handler
    if log_to_file:
        file_handler = get_file_handler(log_file)
        logger.addHandler(file_handler)

    return logger

def get_request_logger()->logging.Logger:
    # get logger specifically for request logging
    return logging.getLogger("fastapi_todo.requests")

