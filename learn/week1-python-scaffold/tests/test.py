import pytest
from datetime import datetime
from src.models.task import Task,Status,Priority

class TestTaskModel:
    def test_create_task_with_default(self):
        task=Task(id=1,title="test task")
        assert task.id==1
        assert task.title=="test task"
        assert task.priority==Priority.MEDIUM
        assert task.status==Status.PENDING
        assert isinstance(task.created_at,datetime)
        assert isinstance(task.updated_at,datetime)

    def test_create_task_with_custom_values(self):
        task=Task(id=2,title="important task",priority=Priority.HIGH,status=Status.IN_PROGRESS)
        assert task.id==2
        assert task.title=="important task"
        assert task.priority==Priority.HIGH
        assert task.status==Status.IN_PROGRESS
        
    def test_task_to_dict(self):
        task_data={
            "id":1,
            "title":"test task",
            "priority":"high",
            "status":"done",
            "created_at":"2024-12-03T10:00:00",
            "updated_at":"2024-12-03T11:00:00"
        }
        task=Task.from_dict(task_data)
        assert task.id==1
        assert task.title=="test task"
        assert task.priority==Priority.HIGH
        assert task.status==Status.DONE

    def test_update_status(self):
        task=Task(id=1,title="test task")
        original_updated_at=task.updated_at

        import time
        time.sleep(0.01)

        task.update_status(Status.DONE)
        assert task.status==Status.DONE
        assert task.updated_at>original_updated_at

    def test_task_str_representation(self):
        task=Task(id=1,title="test task")
        task_str=str(task)
        assert "Task(1)" in task_str
        assert "test task" in task_str
        assert "PENDING" in task_str

    def test_serialization_round_trip(self):
        original_task=Task(id=1,title="test task",priority=Priority.HIGH,status=Status.DONE)

        task_dict=original_task.to_dict()

        restored_task=Task.from_dict(task_dict)

        assert restored_task.id==original_task.id
        assert restored_task.title==original_task.title
        assert restored_task.priority==original_task.priority
        assert restored_task.status==original_task.status