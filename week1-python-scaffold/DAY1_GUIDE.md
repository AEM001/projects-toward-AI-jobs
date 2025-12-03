# Day 1 实战指南：项目初始化 + 数据模型

## 🎯 今日目标
- 搭建完整的项目目录结构
- 创建 Task 数据模型类
- 编写第一个单元测试
- 学习 Python 类、dataclass 和测试基础

**预计时间**: 2-3 小时  
**难度**: ⭐⭐ (入门)

---

## 📚 开始前的准备（30 分钟）

### 1. 阅读学习资料
快速浏览以下文档（不需要全部看完，重点看示例）：
- [Python 类基础](https://docs.python.org/3/tutorial/classes.html) - 看前 3 节
- [dataclass 装饰器](https://docs.python.org/3/library/dataclasses.html) - 看基础示例
- [datetime 模块](https://docs.python.org/3/library/datetime.html) - 了解如何获取当前时间

### 2. 理解项目结构
我们要创建的目录结构：
```
taskmaster/
├── config/
│   └── __init__.py
├── src/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── task.py          # 今天的重点！
│   ├── services/
│   │   └── __init__.py
│   ├── storage/
│   │   └── __init__.py
│   └── utils/
│       └── __init__.py
├── tests/
│   ├── __init__.py
│   └── test_task_model.py   # 今天的重点！
├── .gitignore
└── requirements.txt
```

---

## 🛠️ 实战步骤

### Step 1: 创建项目目录（10 分钟）

```bash
# 1. 进入项目目录
cd /Users/Mac/code/project/week1-python-scaffold

# 2. 创建所有目录
mkdir -p config src/models src/services src/storage src/utils tests docs data logs

# 3. 创建所有 __init__.py 文件（让 Python 识别为包）
touch config/__init__.py
touch src/__init__.py
touch src/models/__init__.py
touch src/services/__init__.py
touch src/storage/__init__.py
touch src/utils/__init__.py
touch tests/__init__.py

# 4. 验证目录结构
使用 ls -R
```

### Step 2: 配置 .gitignore（5 分钟）

创建 `.gitignore` 文件，内容如下：

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# 虚拟环境
venv/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# 项目特定
data/
logs/
*.log

# 测试
.pytest_cache/
.coverage
htmlcov/

# macOS
.DS_Store
```

### Step 3: 创建 requirements.txt（5 分钟）

创建 `requirements.txt` 文件：

```txt
# 测试框架
pytest==7.4.3
pytest-cov==4.1.0

# 日期时间处理
python-dateutil==2.8.2

# 命令行美化（后面会用到）
colorama==0.4.6
tabulate==0.9.0
```

安装依赖：
```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # macOS/Linux

# 安装依赖
pip install -r requirements.txt
```

### Step 4: 创建 Task 数据模型（40 分钟）⭐ 核心

创建 `src/models/task.py` 文件：

```python
"""
Task 数据模型
定义任务的数据结构和基本操作
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TaskPriority(Enum):
    """任务优先级枚举"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class Task:
    """
    任务数据模型
    
    Attributes:
        id: 任务唯一标识符
        title: 任务标题
        priority: 任务优先级
        status: 任务状态
        created_at: 创建时间
        updated_at: 更新时间
    """
    id: int
    title: str
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        """
        将 Task 对象转换为字典（用于 JSON 序列化）
        
        Returns:
            dict: 包含任务所有信息的字典
        """
        return {
            "id": self.id,
            "title": self.title,
            "priority": self.priority.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Task':
        """
        从字典创建 Task 对象（用于 JSON 反序列化）
        
        Args:
            data: 包含任务信息的字典
            
        Returns:
            Task: 新创建的 Task 对象
        """
        return cls(
            id=data["id"],
            title=data["title"],
            priority=TaskPriority(data["priority"]),
            status=TaskStatus(data["status"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"])
        )
    
    def update_status(self, new_status: TaskStatus) -> None:
        """
        更新任务状态
        
        Args:
            new_status: 新的任务状态
        """
        self.status = new_status
        self.updated_at = datetime.now()
    
    def __str__(self) -> str:
        """返回任务的字符串表示"""
        return f"Task({self.id}): {self.title} [{self.status.value}]"
```

**代码讲解**：
1. **Enum 枚举类** - 定义固定的选项（状态、优先级）
2. **@dataclass 装饰器** - 自动生成 `__init__`, `__repr__` 等方法
3. **field(default_factory)** - 为可变类型提供默认值
4. **to_dict/from_dict** - 数据序列化和反序列化
5. **类型注解** - 提高代码可读性和 IDE 支持

### Step 5: 编写单元测试（40 分钟）⭐ 核心

创建 `tests/test_task_model.py` 文件：

```python
"""
Task 模型的单元测试
"""
import pytest
from datetime import datetime
from src.models.task import Task, TaskStatus, TaskPriority


class TestTaskModel:
    """Task 模型测试类"""
    
    def test_create_task_with_defaults(self):
        """测试创建任务（使用默认值）"""
        task = Task(id=1, title="测试任务")
        
        assert task.id == 1
        assert task.title == "测试任务"
        assert task.priority == TaskPriority.MEDIUM
        assert task.status == TaskStatus.PENDING
        assert isinstance(task.created_at, datetime)
        assert isinstance(task.updated_at, datetime)
    
    def test_create_task_with_custom_values(self):
        """测试创建任务（自定义值）"""
        task = Task(
            id=2,
            title="重要任务",
            priority=TaskPriority.HIGH,
            status=TaskStatus.IN_PROGRESS
        )
        
        assert task.id == 2
        assert task.title == "重要任务"
        assert task.priority == TaskPriority.HIGH
        assert task.status == TaskStatus.IN_PROGRESS
    
    def test_task_to_dict(self):
        """测试任务转字典"""
        task = Task(id=1, title="测试任务")
        task_dict = task.to_dict()
        
        assert task_dict["id"] == 1
        assert task_dict["title"] == "测试任务"
        assert task_dict["priority"] == "medium"
        assert task_dict["status"] == "pending"
        assert "created_at" in task_dict
        assert "updated_at" in task_dict
    
    def test_task_from_dict(self):
        """测试从字典创建任务"""
        task_data = {
            "id": 1,
            "title": "测试任务",
            "priority": "high",
            "status": "done",
            "created_at": "2024-12-03T10:00:00",
            "updated_at": "2024-12-03T11:00:00"
        }
        
        task = Task.from_dict(task_data)
        
        assert task.id == 1
        assert task.title == "测试任务"
        assert task.priority == TaskPriority.HIGH
        assert task.status == TaskStatus.DONE
    
    def test_update_status(self):
        """测试更新任务状态"""
        task = Task(id=1, title="测试任务")
        original_updated_at = task.updated_at
        
        # 等待一小段时间，确保时间戳不同
        import time
        time.sleep(0.01)
        
        task.update_status(TaskStatus.DONE)
        
        assert task.status == TaskStatus.DONE
        assert task.updated_at > original_updated_at
    
    def test_task_str_representation(self):
        """测试任务的字符串表示"""
        task = Task(id=1, title="测试任务")
        task_str = str(task)
        
        assert "Task(1)" in task_str
        assert "测试任务" in task_str
        assert "pending" in task_str
    
    def test_serialization_round_trip(self):
        """测试序列化和反序列化的完整流程"""
        # 创建任务
        original_task = Task(
            id=1,
            title="测试任务",
            priority=TaskPriority.HIGH,
            status=TaskStatus.IN_PROGRESS
        )
        
        # 转为字典
        task_dict = original_task.to_dict()
        
        # 从字典恢复
        restored_task = Task.from_dict(task_dict)
        
        # 验证数据一致
        assert restored_task.id == original_task.id
        assert restored_task.title == original_task.title
        assert restored_task.priority == original_task.priority
        assert restored_task.status == original_task.status
```

**测试讲解**：
1. **测试类组织** - 使用 `TestXxx` 类组织相关测试
2. **测试方法命名** - `test_xxx` 清晰描述测试内容
3. **assert 断言** - 验证预期结果
4. **测试覆盖** - 测试正常情况、边界情况、完整流程

### Step 6: 运行测试（10 分钟）

```bash
# 运行所有测试
pytest tests/

# 运行特定测试文件
pytest tests/test_task_model.py

# 详细输出
pytest tests/test_task_model.py -v

# 查看测试覆盖率
pytest tests/test_task_model.py --cov=src/models --cov-report=term-missing
```

**预期输出**：
```
======================== test session starts ========================
collected 8 items

tests/test_task_model.py ........                            [100%]

======================== 8 passed in 0.05s =========================
```

### Step 7: 初始化 Git 仓库（10 分钟）

```bash
# 初始化 Git
git init

# 添加所有文件
git add .

# 第一次提交
git commit -m "feat: 初始化项目结构和 Task 数据模型

- 创建项目目录结构
- 实现 Task 数据模型（支持序列化/反序列化）
- 添加 TaskStatus 和 TaskPriority 枚举
- 编写完整的单元测试（8个测试用例）
- 配置 .gitignore 和 requirements.txt"

# 查看提交历史
git log --oneline
```

---

## ✅ 今日成果检查

完成后，你应该有：

### 文件清单
- [x] 完整的项目目录结构
- [x] `.gitignore` 文件
- [x] `requirements.txt` 文件
- [x] `src/models/task.py` - Task 模型（约 100 行）
- [x] `tests/test_task_model.py` - 测试文件（约 120 行）

### 功能验证
```bash
# 1. 测试通过
pytest tests/test_task_model.py
# 应该看到：8 passed

# 2. 可以导入模块
python3 -c "from src.models.task import Task; print('导入成功')"

# 3. 创建任务测试
python3 -c "
from src.models.task import Task, TaskPriority
task = Task(id=1, title='测试', priority=TaskPriority.HIGH)
print(task)
print(task.to_dict())
"
```

### 学习收获
- [x] 理解 Python 项目的标准结构
- [x] 学会使用 dataclass 创建数据模型
- [x] 掌握 Enum 枚举类型的使用
- [x] 学会编写单元测试
- [x] 了解数据序列化和反序列化
- [x] 学会使用 Git 进行版本控制

---

## 💡 常见问题

### Q1: 为什么要用 dataclass？
**A**: dataclass 自动生成 `__init__`, `__repr__` 等方法，减少样板代码，让你专注于业务逻辑。

### Q2: Enum 有什么用？
**A**: Enum 限制了可选值，避免拼写错误（如 "peding" vs "pending"），提高代码安全性。

### Q3: 测试为什么重要？
**A**: 测试是代码质量的保障，能及早发现 bug，方便重构，也是最好的文档。

### Q4: 为什么要用虚拟环境？
**A**: 隔离项目依赖，避免不同项目之间的包冲突。

### Q5: 如果测试失败怎么办？
**A**: 
1. 仔细阅读错误信息
2. 检查导入路径是否正确
3. 确认虚拟环境已激活
4. 使用 `python -m pytest` 而不是 `pytest`

---

## 📝 今日总结

在 Day 1，你完成了：
1. ✅ 搭建了标准的 Python 项目结构
2. ✅ 创建了第一个数据模型 Task
3. ✅ 编写了 8 个单元测试
4. ✅ 学会了使用 pytest 运行测试
5. ✅ 初始化了 Git 仓库

**明天预告（Day 2）**：
- 实现 JSON 数据持久化
- 学习文件操作和异常处理
- 让任务数据可以保存到文件

---

## 🎯 作业（可选）

1. **扩展 Task 模型**：添加 `description` 字段（任务描述）
2. **添加测试**：测试无效的优先级和状态
3. **探索 dataclass**：尝试使用 `frozen=True` 创建不可变对象
4. **学习 pytest**：了解 pytest 的 fixture 功能

---

**恭喜完成 Day 1！休息一下，明天继续！** 🎉
