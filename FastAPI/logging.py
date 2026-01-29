import logging
import sys
from pathlib import Path

def get_log_formatter()->logging.Formatter:
    return logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

def get_log_handler()->logging.Handler:
    handler=logging.StreamHandler(sys.stdout)