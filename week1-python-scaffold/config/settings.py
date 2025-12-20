
from pathlib import Path


APP_NAME = "taskmaster"

BASE_DIR = Path(__file__).resolve().parent.parent

LOG_LEVEL = "INFO"
LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / f"{APP_NAME}.log"
LOG_TO_CONSOLE = False

DATA_FILE = BASE_DIR / "data" / "task.json"
