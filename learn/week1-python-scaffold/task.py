from config.logging_config import setup_logging
from config import settings
from src.storage.json_storage import JSONStorage
from src.services.task_service import TaskService
from src.cli import TaskCLI


def main() -> int:
    setup_logging()
    storage = JSONStorage(settings.DATA_FILE)
    service = TaskService(storage)
    cli = TaskCLI(service)
    return cli.run()


if __name__ == "__main__":
    raise SystemExit(main())
