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
        assert isinstance(temp_storage.file_path,Path)

    def test_save_empty_list(self,temp_storage):
        # 保存任务
        temp_storage.save([])
        assert temp_storage.exists()
        
        # 加载任务
        loaded_tasks = temp_storage.load()
        
        # 验证数量
        assert len(loaded_tasks) == 0

    def test_load_nonexistent_file(self, temp_storage):
        """测试加载不存在的文件"""
        # 文件不存在时应返回空列表
        loaded = temp_storage.load()
        assert loaded == []
        assert not temp_storage.exists()
    
    def test_save_overwrites_existing_file(self, temp_storage, sample_tasks):
        """测试保存会覆盖已有文件"""
        # 第一次保存
        temp_storage.save(sample_tasks)
        
        # 第二次保存（只有一个任务）
        new_task = [Task(id=99, title="新任务")]
        temp_storage.save(new_task)
        
        # 验证只有新任务
        loaded = temp_storage.load()
        assert len(loaded) == 1
        assert loaded[0].id == 99
    
    def test_json_file_format(self, temp_storage, sample_tasks):
        """测试 JSON 文件格式正确"""
        temp_storage.save(sample_tasks)
        
        # 直接读取 JSON 文件验证格式
        with open(temp_storage.file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert isinstance(data, list)
        assert len(data) == 3
        assert "id" in data[0]
        assert "title" in data[0]
        assert "priority" in data[0]
        assert "status" in data[0]
    
    def test_load_corrupted_json(self, temp_storage):
        """测试加载损坏的 JSON 文件"""
        # 写入无效的 JSON
        with open(temp_storage.file_path, 'w') as f:
            f.write("这不是有效的 JSON")
        
        # 应该抛出 ValueError
        with pytest.raises(ValueError):
            temp_storage.load()
    
    def test_load_invalid_task_data(self, temp_storage):
        """测试加载缺少字段的任务数据"""
        # 写入缺少必要字段的数据
        invalid_data = [{"id": 1}]  # 缺少 title 等字段
        with open(temp_storage.file_path, 'w') as f:
            json.dump(invalid_data, f)
        
        # 应该抛出 ValueError
        with pytest.raises(ValueError):
            temp_storage.load()
    
    def test_clear_storage(self, temp_storage, sample_tasks):
        """测试清空存储"""
        temp_storage.save(sample_tasks)
        assert temp_storage.exists()
        
        temp_storage.clear()
        assert not temp_storage.exists()
    
    def test_get_file_path(self, temp_storage):
        """测试获取文件路径"""
        path = temp_storage.get_file_path()
        assert isinstance(path, str)
        assert "test_tasks.json" in path
    
    def test_directory_creation(self, tmp_path):
        """测试自动创建目录"""
        # 使用不存在的多级目录
        nested_path = tmp_path / "level1" / "level2" / "tasks.json"
        storage = JSONStorage(str(nested_path))
        
        # 保存时应该自动创建目录
        storage.save([Task(id=1, title="测试")])
        assert storage.exists()
        assert nested_path.parent.exists()

