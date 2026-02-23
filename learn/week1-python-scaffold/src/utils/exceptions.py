from __future__ import annotations


class TaskMasterException(Exception):
    pass


class TaskNotFoundException(TaskMasterException):
    def __init__(self, task_id: str):
        self.task_id = str(task_id)
        super().__init__(f"Task not found: {self.task_id}")


class InvalidTaskStatusException(TaskMasterException):
    def __init__(self, status):
        self.status = status
        super().__init__(f"Invalid task status: {status}")


class StorageException(TaskMasterException):
    def __init__(self, message: str, *, operation: str | None = None, path: str | None = None):
        self.operation = operation
        self.path = path
        super().__init__(message)
