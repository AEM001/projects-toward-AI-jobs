import pytest
import json
from pathlib import Path
from src.storage.json_storage import JSONStorage
from src.models.task import Task,Status,Priority
# 测试任务：新建任务，保存，读取，修改
class TestJSONStorage:

    @pytest.fixture
    def temp_storage(self,tmp_path):
        storage_file=tmp_path /"test_tasks.json"
        storage=JSONStorage(str(storage_file))
        yield storage
        # if storage.exists():
        storage.clear()
    
    @pytest.fixture
    def sample_tasks(self):
        return [
            Task(1,"任务1",Priority.HIGH),
            Task(2,"任务2",Priority.MEDIUM,Status.DONE),
            Task(3,"任务3",Priority.LOW)
        ]
    
    def test_storage_initialization(self,temp_storage):
        assert temp_storage is not None
        assert temp_storage.load()==[]
        assert isinstance(temp_storage.file_path,Path)

    def test_save_empty_list(self,temp_storage):
        temp_storage.save([])
        assert temp_storage.exists()
        loaded_tasks = temp_storage.load()
        assert len(loaded_tasks) == 0

    def test_load_nonexistent_file(self, temp_storage):
        loaded = temp_storage.load()
        assert loaded == []
        assert not temp_storage.exists()
    
    def test_save_overwrites_existing_file(self, temp_storage, sample_tasks):
        temp_storage.save(sample_tasks)
        new_task = [Task(id=99, title="新任务")]
        temp_storage.save(new_task)
        loaded = temp_storage.load()
        assert len(loaded) == 1
        assert loaded[0].id == 99
    
    def test_json_file_format(self, temp_storage, sample_tasks):
        temp_storage.save(sample_tasks)
        with open(temp_storage.file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert isinstance(data, list)
        assert len(data) == 3
        assert "id" in data[0]
        assert "title" in data[0]
        assert "priority" in data[0]
        assert "status" in data[0]
    
    def test_load_corrupted_json(self, temp_storage):
        with open(temp_storage.file_path, 'w') as f:
            f.write("这不是有效的 JSON")
        with pytest.raises(ValueError):
            temp_storage.load()
    
    def test_load_invalid_task_data(self, temp_storage):
        invalid_data = [{"id": 1}]  # 缺少 title 等字段
        with open(temp_storage.file_path, 'w') as f:
            json.dump(invalid_data, f)
        
        with pytest.raises(ValueError):
            temp_storage.load()
    
    def test_clear_storage(self, temp_storage, sample_tasks):
        temp_storage.save(sample_tasks)
        assert temp_storage.exists()
        
        temp_storage.clear()
        assert not temp_storage.exists()
    
    def test_get_file_path(self, temp_storage):
        path = temp_storage.get_file_path()
        assert isinstance(path, str)
        assert "test_tasks.json" in path
    
    def test_directory_creation(self, tmp_path):
        nested_path = tmp_path / "level1" / "level2" / "tasks.json"
        storage = JSONStorage(str(nested_path))
        storage.save([Task(id=1, title="测试")])
        assert storage.exists()
        assert nested_path.parent.exists()

