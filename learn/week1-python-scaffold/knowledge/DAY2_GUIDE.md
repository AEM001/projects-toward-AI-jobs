# Day 2 实战指南：数据持久化

## 🎯 今日目标
- 实现 JSON 文件存储功能
- 学习 Python 文件操作（读写）
- 掌握异常处理基础
- 理解数据序列化和反序列化
- 让任务数据可以保存和恢复

**预计时间**: 2-3 小时  
**难度**: ⭐⭐⭐ (进阶)

---

## 📚 开始前的准备（30 分钟）

### 1. 回顾 Day 1
确保你已经完成：
- [x] Task 模型创建完成
- [x] 测试全部通过
- [x] 理解了 `to_dict()` 和 `from_dict()` 方法

### 2. 阅读学习资料
快速浏览以下文档：
- [JSON 模块](https://docs.python.org/3/library/json.html) - 看基础示例
- [文件操作](https://docs.python.org/3/tutorial/inputoutput.html#reading-and-writing-files) - 看 with 语句
- [pathlib 模块](https://docs.python.org/3/library/pathlib.html) - 现代化的路径操作
- [异常处理](https://docs.python.org/3/tutorial/errors.html) - try/except 基础

### 3. 今日核心概念
- **JSON**: JavaScript Object Notation，轻量级数据交换格式
- **序列化**: 把 Python 对象转换为 JSON 字符串
- **反序列化**: 把 JSON 字符串转换回 Python 对象
- **文件 I/O**: Input/Output，读写文件操作
- **异常处理**: 处理程序运行时可能出现的错误

---

## 🛠️ 实战步骤

### Step 1: 理解存储需求（10 分钟）

我们需要实现什么？
```python
# 保存多个任务到文件
tasks = [task1, task2, task3]
storage.save(tasks)  # 保存到 data/tasks.json

# 从文件读取任务
loaded_tasks = storage.load()  # 返回任务列表
```

**JSON 文件格式示例**：
```json
[
  {
    "id": 1,
    "title": "学习 Python",
    "priority": "high",
    "status": "pending",
    "created_at": "2024-12-03T10:00:00",
    "updated_at": "2024-12-03T10:00:00"
  },
  {
    "id": 2,
    "title": "写代码",
    "priority": "medium",
    "status": "in_progress",
    "created_at": "2024-12-03T11:00:00",
    "updated_at": "2024-12-03T11:00:00"
  }
]
```

### Step 2: 创建存储模块（50 分钟）⭐ 核心

创建 `src/storage/json_storage.py` 文件：

```python
"""
JSON 存储模块
负责任务数据的持久化（保存和读取）
"""
import json
from pathlib import Path
from typing import List, Optional
from src.models.task import Task


class JSONStorage:
    """
    JSON 文件存储类
    
    负责将任务列表保存到 JSON 文件，以及从文件中读取任务
    """
    
    def __init__(self, file_path: str = "data/tasks.json"):
        """
        初始化存储对象
        
        Args:
            file_path: JSON 文件路径，默认为 data/tasks.json
        """
        self.file_path = Path(file_path)
        # 确保 data 目录存在
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
    
    def save(self, tasks: List[Task]) -> None:
        """
        保存任务列表到 JSON 文件
        
        Args:
            tasks: 要保存的任务列表
            
        Raises:
            IOError: 文件写入失败时抛出
        """
        try:
            # 将所有任务转换为字典
            tasks_data = [task.to_dict() for task in tasks]
            
            # 写入 JSON 文件
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(tasks_data, f, ensure_ascii=False, indent=2)
                
        except IOError as e:
            raise IOError(f"保存任务失败: {e}")
        except Exception as e:
            raise Exception(f"保存任务时发生未知错误: {e}")
    
    def load(self) -> List[Task]:
        """
        从 JSON 文件加载任务列表
        
        Returns:
            List[Task]: 任务对象列表，如果文件不存在返回空列表
            
        Raises:
            ValueError: JSON 格式错误时抛出
            IOError: 文件读取失败时抛出
        """
        # 如果文件不存在，返回空列表
        if not self.file_path.exists():
            return []
        
        try:
            # 读取 JSON 文件
            with open(self.file_path, 'r', encoding='utf-8') as f:
                tasks_data = json.load(f)
            
            # 将字典列表转换为 Task 对象列表
            tasks = [Task.from_dict(data) for data in tasks_data]
            return tasks
            
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON 格式错误: {e}")
        except IOError as e:
            raise IOError(f"读取任务失败: {e}")
        except KeyError as e:
            raise ValueError(f"任务数据缺少必要字段: {e}")
        except Exception as e:
            raise Exception(f"加载任务时发生未知错误: {e}")
    
    def exists(self) -> bool:
        """
        检查存储文件是否存在
        
        Returns:
            bool: 文件存在返回 True，否则返回 False
        """
        return self.file_path.exists()
    
    def clear(self) -> None:
        """
        清空存储文件（删除文件）
        
        主要用于测试
        """
        if self.file_path.exists():
            self.file_path.unlink()
    
    def get_file_path(self) -> str:
        """
        获取存储文件的完整路径
        
        Returns:
            str: 文件路径字符串
        """
        return str(self.file_path.absolute())
```

**代码讲解**：

1. **Path 对象** - 现代化的路径操作，比字符串拼接更安全
   ```python
   self.file_path = Path("data/tasks.json")
   self.file_path.parent.mkdir(parents=True, exist_ok=True)
   ```

2. **with 语句** - 自动管理文件打开和关闭
   ```python
   with open(file_path, 'w', encoding='utf-8') as f:
       json.dump(data, f)
   # 离开 with 块后，文件自动关闭
   ```

3. **异常处理** - 捕获可能的错误并给出友好提示
   ```python
   try:
       # 可能出错的代码
   except IOError as e:
       # 处理 IO 错误
   except Exception as e:
       # 处理其他错误
   ```

4. **列表推导式** - 简洁的列表转换
   ```python
   tasks_data = [task.to_dict() for task in tasks]
   # 等价于：
   # tasks_data = []
   # for task in tasks:
   #     tasks_data.append(task.to_dict())
   ```

5. **json.dump() 参数**：
   - `ensure_ascii=False` - 允许中文字符
   - `indent=2` - 格式化输出，缩进 2 个空格

### Step 3: 编写存储层测试（50 分钟）⭐ 核心

创建 `tests/test_storage.py` 文件：

```python
"""
存储层的单元测试
"""
import pytest
import json
from pathlib import Path
from src.storage.json_storage import JSONStorage
from src.models.task import Task, Status, Priority


class TestJSONStorage:
    """JSON 存储测试类"""
    
    @pytest.fixture
    def temp_storage(self, tmp_path):
        """
        创建临时存储对象（pytest fixture）
        
        tmp_path 是 pytest 提供的临时目录
        """
        storage_file = tmp_path / "test_tasks.json"
        storage = JSONStorage(str(storage_file))
        yield storage
        # 测试结束后清理
        if storage.exists():
            storage.clear()
    
    @pytest.fixture
    def sample_tasks(self):
        """创建示例任务列表"""
        return [
            Task(id=1, title="任务1", priority=Priority.HIGH),
            Task(id=2, title="任务2", priority=Priority.MEDIUM, status=Status.DONE),
            Task(id=3, title="任务3", priority=Priority.LOW)
        ]
    
    def test_storage_initialization(self, temp_storage):
        """测试存储对象初始化"""
        assert temp_storage is not None
        assert isinstance(temp_storage.file_path, Path)
    
    def test_save_empty_list(self, temp_storage):
        """测试保存空任务列表"""
        temp_storage.save([])
        assert temp_storage.exists()
        
        # 验证文件内容
        loaded = temp_storage.load()
        assert loaded == []
    
    def test_save_and_load_tasks(self, temp_storage, sample_tasks):
        """测试保存和加载任务"""
        # 保存任务
        temp_storage.save(sample_tasks)
        assert temp_storage.exists()
        
        # 加载任务
        loaded_tasks = temp_storage.load()
        
        # 验证数量
        assert len(loaded_tasks) == 3
        
        # 验证第一个任务
        assert loaded_tasks[0].id == 1
        assert loaded_tasks[0].title == "任务1"
        assert loaded_tasks[0].priority == Priority.HIGH
        assert loaded_tasks[0].status == Status.PENDING
        
        # 验证第二个任务
        assert loaded_tasks[1].id == 2
        assert loaded_tasks[1].status == Status.DONE
    
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
```

**测试讲解**：

1. **pytest fixture** - 测试前的准备工作
   ```python
   @pytest.fixture
   def temp_storage(self, tmp_path):
       # tmp_path 是 pytest 提供的临时目录
       storage = JSONStorage(str(tmp_path / "test.json"))
       yield storage  # 返回给测试函数
       # 测试后的清理工作
   ```

2. **测试异常** - 验证错误处理
   ```python
   with pytest.raises(ValueError):
       storage.load()  # 应该抛出 ValueError
   ```

3. **测试覆盖** - 测试各种场景：
   - 正常情况（保存、加载）
   - 边界情况（空列表、不存在的文件）
   - 异常情况（损坏的 JSON、缺少字段）

### Step 4: 运行测试（10 分钟）

```bash
# 激活虚拟环境
source venv/bin/activate

# 运行存储层测试
pytest tests/test_storage.py -v

# 运行所有测试
pytest tests/ -v

# 查看测试覆盖率
pytest tests/test_storage.py --cov=src/storage --cov-report=term-missing
```

**预期输出**：
```
tests/test_storage.py::TestJSONStorage::test_storage_initialization PASSED
tests/test_storage.py::TestJSONStorage::test_save_empty_list PASSED
tests/test_storage.py::TestJSONStorage::test_save_and_load_tasks PASSED
tests/test_storage.py::TestJSONStorage::test_load_nonexistent_file PASSED
tests/test_storage.py::TestJSONStorage::test_save_overwrites_existing_file PASSED
tests/test_storage.py::TestJSONStorage::test_json_file_format PASSED
tests/test_storage.py::TestJSONStorage::test_load_corrupted_json PASSED
tests/test_storage.py::TestJSONStorage::test_load_invalid_task_data PASSED
tests/test_storage.py::TestJSONStorage::test_clear_storage PASSED
tests/test_storage.py::TestJSONStorage::test_get_file_path PASSED
tests/test_storage.py::TestJSONStorage::test_directory_creation PASSED

======================== 11 passed in 0.15s =========================
```

### Step 5: 手动测试存储功能（15 分钟）

创建一个测试脚本 `test_manual.py`（临时文件，不提交）：

```python
"""
手动测试存储功能
"""
from src.models.task import Task, Priority, Status
from src.storage.json_storage import JSONStorage

def main():
    # 创建存储对象
    storage = JSONStorage("data/tasks.json")
    
    # 创建一些任务
    tasks = [
        Task(id=1, title="学习 Python 文件操作", priority=Priority.HIGH),
        Task(id=2, title="实现 JSON 存储", priority=Priority.MEDIUM, status=Status.IN_PROGRESS),
        Task(id=3, title="编写单元测试", priority=Priority.LOW)
    ]
    
    print("=" * 50)
    print("1. 保存任务到文件")
    print("=" * 50)
    storage.save(tasks)
    print(f"✅ 已保存 {len(tasks)} 个任务到: {storage.get_file_path()}")
    
    print("\n" + "=" * 50)
    print("2. 从文件加载任务")
    print("=" * 50)
    loaded_tasks = storage.load()
    print(f"✅ 已加载 {len(loaded_tasks)} 个任务")
    
    print("\n任务列表:")
    for task in loaded_tasks:
        print(f"  - {task}")
    
    print("\n" + "=" * 50)
    print("3. 修改任务状态并保存")
    print("=" * 50)
    loaded_tasks[0].update_status(Status.DONE)
    storage.save(loaded_tasks)
    print("✅ 任务状态已更新并保存")
    
    print("\n" + "=" * 50)
    print("4. 验证修改已保存")
    print("=" * 50)
    reloaded_tasks = storage.load()
    print(f"第一个任务状态: {reloaded_tasks[0].status.value}")
    
    print("\n✅ 所有测试通过！")

if __name__ == "__main__":
    main()
```

运行测试：
```bash
python test_manual.py
```

查看生成的 JSON 文件：
```bash
cat data/tasks.json
```

### Step 6: Git 提交（10 分钟）

```bash
# 查看修改
git status

# 添加新文件
git add src/storage/json_storage.py
git add tests/test_storage.py

# 提交
git commit -m "feat: 实现 JSON 数据持久化

- 创建 JSONStorage 类，支持任务的保存和加载
- 实现完整的异常处理（IOError, ValueError）
- 使用 pathlib 进行路径操作
- 自动创建数据目录
- 编写 11 个单元测试，覆盖各种场景
- 测试覆盖率达到 100%"

# 查看提交历史
git log --oneline
```

---

## ✅ 今日成果检查

### 文件清单
- [x] `src/storage/json_storage.py` - 存储类（约 120 行）
- [x] `tests/test_storage.py` - 测试文件（约 150 行）
- [x] `data/tasks.json` - 数据文件（运行后生成）

### 功能验证

**测试 1: 保存和加载**
```python
from src.models.task import Task, Priority
from src.storage.json_storage import JSONStorage

storage = JSONStorage("data/test.json")
tasks = [Task(id=1, title="测试", priority=Priority.HIGH)]
storage.save(tasks)
loaded = storage.load()
print(loaded[0])  # 应该输出: Task(1): 测试 [PENDING]
```

**测试 2: 文件不存在**
```python
storage = JSONStorage("data/nonexistent.json")
tasks = storage.load()
print(tasks)  # 应该输出: []
```

**测试 3: 数据持久化**
```bash
# 运行两次，验证数据保存
python test_manual.py
python test_manual.py  # 第二次运行应该能读取之前的数据
```

### 学习收获
- [x] 掌握 JSON 序列化和反序列化
- [x] 学会使用 pathlib 进行路径操作
- [x] 理解文件 I/O 操作（读写）
- [x] 掌握异常处理（try/except）
- [x] 学会使用 pytest fixture
- [x] 理解测试驱动开发（TDD）

---

## 💡 常见问题

### Q1: 为什么用 pathlib 而不是字符串拼接路径？
**A**: pathlib 更安全、更现代化，自动处理不同操作系统的路径分隔符（Windows 用 `\`，Linux/Mac 用 `/`）。

```python
# 不推荐
path = "data" + "/" + "tasks.json"

# 推荐
path = Path("data") / "tasks.json"
```

### Q2: with 语句有什么好处？
**A**: 自动管理资源（文件、数据库连接等），即使发生异常也会正确关闭文件。

```python
# 不推荐
f = open("file.txt", "w")
f.write("data")
f.close()  # 如果 write 出错，close 不会执行

# 推荐
with open("file.txt", "w") as f:
    f.write("data")
# 自动关闭，即使出错
```

### Q3: 为什么要测试异常情况？
**A**: 真实环境中会遇到各种错误（文件损坏、权限不足等），测试异常处理确保程序健壮性。

### Q4: json.dump() 和 json.dumps() 有什么区别？
**A**: 
- `json.dump(obj, file)` - 直接写入文件
- `json.dumps(obj)` - 返回 JSON 字符串

```python
# dump - 写入文件
with open("data.json", "w") as f:
    json.dump(data, f)

# dumps - 返回字符串
json_str = json.dumps(data)
print(json_str)
```

### Q5: 测试时如何避免污染真实数据？
**A**: 使用 pytest 的 `tmp_path` fixture，它会创建临时目录，测试结束后自动清理。

---

## 🔍 深入理解

### 1. 异常处理的层次
```python
try:
    # 可能出错的代码
    data = json.load(f)
except json.JSONDecodeError as e:
    # 处理特定错误
    print(f"JSON 格式错误: {e}")
except IOError as e:
    # 处理 IO 错误
    print(f"文件读取失败: {e}")
except Exception as e:
    # 处理其他所有错误
    print(f"未知错误: {e}")
finally:
    # 无论是否出错都会执行
    print("清理工作")
```

### 2. 列表推导式的威力
```python
# 传统方式
tasks_data = []
for task in tasks:
    tasks_data.append(task.to_dict())

# 列表推导式（更简洁）
tasks_data = [task.to_dict() for task in tasks]

# 带条件的列表推导式
high_priority = [t for t in tasks if t.priority == Priority.HIGH]
```

### 3. Path 对象的常用操作
```python
from pathlib import Path

path = Path("data/tasks.json")

# 获取父目录
path.parent  # Path("data")

# 获取文件名
path.name  # "tasks.json"

# 检查存在
path.exists()  # True/False

# 创建目录
path.parent.mkdir(parents=True, exist_ok=True)

# 删除文件
path.unlink()

# 读取文件
content = path.read_text()

# 写入文件
path.write_text("content")
```

---

## 📝 今日总结

在 Day 2，你完成了：
1. ✅ 实现了 JSONStorage 存储类
2. ✅ 掌握了文件读写操作
3. ✅ 学会了异常处理
4. ✅ 理解了数据持久化
5. ✅ 编写了 11 个单元测试
6. ✅ 测试覆盖率达到 100%

**关键成就**：
- 任务数据现在可以保存到文件了！
- 程序重启后数据不会丢失
- 具备完善的错误处理能力

**明天预告（Day 3）**：
- 实现 TaskService 业务逻辑层
- 完成任务的增删改查（CRUD）
- 自动生成任务 ID
- 实现任务筛选和查询

---

## 🎯 作业（可选）

1. **添加备份功能**：实现 `backup()` 方法，将当前数据备份到 `tasks_backup.json`
2. **实现导出功能**：添加 `export_to_csv()` 方法，导出为 CSV 格式
3. **添加统计功能**：实现 `get_stats()` 返回任务统计信息（总数、完成数等）
4. **探索其他格式**：尝试使用 YAML 或 TOML 格式存储

### 作业示例代码

```python
# 作业 1: 备份功能
def backup(self) -> str:
    """
    备份当前数据
    
    Returns:
        str: 备份文件路径
    """
    import shutil
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = self.file_path.parent / f"tasks_backup_{timestamp}.json"
    
    if self.exists():
        shutil.copy(self.file_path, backup_path)
        return str(backup_path)
    return ""
```

---

**恭喜完成 Day 2！你已经掌握了数据持久化的核心技能！** 🎉

**小贴士**：休息一下，回顾今天学到的内容，明天我们将实现更强大的业务逻辑层！
