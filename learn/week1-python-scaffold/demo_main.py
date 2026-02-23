from config.logging_config import setup_logging
from config import settings
from src.services.task_service import TaskService
from src.storage.json_storage import JSONStorage
from src.models.task import Status
from src.utils.exceptions import TaskMasterException
from src.utils.logger import get_logger


def main() -> None:
    setup_logging()
    logger=get_logger()

    storage=JSONStorage(str(settings.DATA_FILE))
    service=TaskService(storage)

    try:
        t1 = service.add_task("learn logging")
        logger.info("created task: %s", t1.to_dict())

        service.update_task_status(t1.id, Status.DONE)
        logger.info("updated task status to done: %s", service.get_task(t1.id).to_dict())

        logger.info("all tasks: %s", [t.to_dict() for t in service.list_tasks()])

        service.get_task("not-exist")
        service.delete_task("not-exist")
        
    except TaskMasterException as e:
        logger.warning("caught expected TaskMasterException: %s", e, exc_info=True)


if __name__ == "__main__":
    main()
