import pytest

from src.models.task import Status, Priority
from src.services.task_service import TaskService
from src.storage.json_storage import JSONStorage
from src.utils.exceptions import TaskNotFoundException


class TestTaskService:
    @pytest.fixture
    def service(self, tmp_path):
        storage_file = tmp_path / "tasks.json"
        storage = JSONStorage(str(storage_file))
        return TaskService(storage)

    def test_add_task_success(self, service):
        task = service.add_task("hello", Priority.HIGH)
        assert task.id is not None
        assert task.title == "hello"
        assert task.priority == Priority.HIGH
        assert task.status == Status.PENDING

        tasks = service.list_tasks()
        assert len(tasks) == 1
        assert str(tasks[0].id) == str(task.id)

    def test_add_task_empty_title_raises(self, service):
        with pytest.raises(ValueError):
            service.add_task("   ")

    def test_get_task_success(self, service):
        created = service.add_task("t1")
        fetched = service.get_task(created.id)
        assert str(fetched.id) == str(created.id)
        assert fetched.title == "t1"

    def test_get_task_not_found_raises(self, service):
        with pytest.raises(TaskNotFoundException):
            service.get_task("not-exist")

    def test_list_tasks_filter_by_status(self, service):
        t1 = service.add_task("t1")
        t2 = service.add_task("t2")

        service.update_task_status(t1.id, Status.DONE)

        done = service.list_tasks(Status.DONE)
        pending = service.list_tasks(Status.PENDING)

        assert len(done) == 1
        assert str(done[0].id) == str(t1.id)

        assert len(pending) == 1
        assert str(pending[0].id) == str(t2.id)

    def test_update_task_status_success(self, service):
        task = service.add_task("t1")
        old_updated_at = task.updated_at

        updated = service.update_task_status(task.id, Status.DONE)
        assert updated.status == Status.DONE
        assert updated.updated_at >= old_updated_at

        fetched = service.get_task(task.id)
        assert fetched.status == Status.DONE

    def test_update_task_status_not_found_raises(self, service):
        with pytest.raises(TaskNotFoundException):
            service.update_task_status("not-exist", Status.DONE)

    def test_delete_task_success(self, service):
        t1 = service.add_task("t1")
        t2 = service.add_task("t2")

        service.delete_task(t1.id)
        tasks = service.list_tasks()
        assert len(tasks) == 1
        assert str(tasks[0].id) == str(t2.id)

        with pytest.raises(TaskNotFoundException):
            service.get_task(t1.id)

    def test_delete_task_not_found_raises(self, service):
        with pytest.raises(TaskNotFoundException):
            service.delete_task("not-exist")
