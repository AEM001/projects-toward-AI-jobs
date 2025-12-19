# import task, storage
import uuid
from typing import List, Optional

from src.models.task import Task, Priority, Status
from src.storage.json_storage import JSONStorage


class TaskService:
    def __init__(self, storage: JSONStorage):
        self.storage = storage
        # NOTE: 不把 tasks 缓存在内存里；每次操作都从 storage.load() 读取“权威数据”，避免不同步

    def add_task(self, title: str, priority: Priority = Priority.MEDIUM) -> Task:  # remember this grammar
        # NOTE: Service 层统一做输入校验，CLI/其他调用方就能复用同一套规则
        if title is None:
            raise ValueError("title is required")
        cleaned_title = title.strip()
        if not cleaned_title:
            raise ValueError("title cannot be empty")

        task_id = uuid.uuid4().hex  # NOTE: 使用 UUID 生成唯一 id
        tasks = self.storage.load()  # NOTE: load -> modify -> save

        new_task = Task(id=task_id, title=cleaned_title, priority=priority)
        tasks.append(new_task)
        self.storage.save(tasks)
        return new_task

    def get_task(self, task_id: str) -> Task:
        tasks = self.storage.load()
        for task in tasks:
            if str(task.id) == str(task_id):
                return task
        # NOTE: 找不到任务时统一抛异常（Day3 推荐），而不是返回字符串
        raise ValueError(f"Task not found: {task_id}")

    # def list_tasks(self,):
    def list_tasks(self, status: Optional[Status] = None) -> List[Task]:
        tasks = self.storage.load()
        if status is None:
            return tasks
        return [t for t in tasks if t.status == status]

    def update_task_status(self, task_id: str, status: Status) -> Task:
        tasks = self.storage.load()
        for task in tasks:
            if str(task.id) == str(task_id):
                # NOTE: 复用 Task.update_status，确保 updated_at 同步更新
                task.update_status(status)
                self.storage.save(tasks)
                return task
        raise ValueError(f"Task not found: {task_id}")

    def delete_task(self, task_id: str) -> None:
        tasks = self.storage.load()
        new_tasks = [t for t in tasks if str(t.id) != str(task_id)]
        if len(new_tasks) == len(tasks):
            raise ValueError(f"Task not found: {task_id}")
        self.storage.save(new_tasks)