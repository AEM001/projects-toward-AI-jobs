# Day 3 实战指南：业务逻辑层（TaskService）

## 🎯 今日目标
- 实现 `TaskService` 业务逻辑层（CRUD）
- 实现自动 ID 生成（UUID）
- 学会在 Service 层做“校验 + 查找 + 状态变更”的统一入口
- 编写业务逻辑层的单元测试（不依赖 CLI）

**预计时间**: 2-3 小时  
**难度**: ⭐⭐⭐ (进阶)

---

## 📚 开始前的准备（30 分钟）

### 1. 回顾 Day 1 & Day 2
确保你已经完成：
- [x] `Task` 模型可以 `to_dict()` / `from_dict()`
- [x] `JSONStorage` 可以 `save()` / `load()`
- [x] 能用 pytest 运行测试

### 2. 阅读学习资料
快速浏览以下文档：
- [UUID 模块](https://docs.python.org/3/library/uuid.html) - 重点看 `uuid4()`
- [列表推导式](https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions) - 用于筛选任务
- [filter() 函数](https://docs.python.org/3/library/functions.html#filter) - 了解即可（建议优先用列表推导式）

### 3. 今日核心概念
- **Service 层**: 业务规则集中管理（而不是散落在 CLI、Storage 或 Model 里）
- **CRUD**:
  - Create（新增）
  - Read（查询）
  - Update（更新）
  - Delete（删除）
- **ID 生成策略**: UUID（推荐）或自增 ID（需要额外维护计数器）
- **数据流**（建议你记住这个顺序）:
  - `service` 调用 `storage.load()` 拿到任务列表
  - `service` 在内存里完成查找/校验/修改
  - `service` 调用 `storage.save()` 持久化

---

## 🛠️ 实战步骤

### Step 1: 明确 Service 的职责（10 分钟）

你今天要做的 `TaskService`，应该负责：
- 管理“任务列表”这一份权威数据
- 对外提供**稳定接口**：`add_task/get_task/list_tasks/update_task_status/delete_task`
- 做输入校验（标题不能为空、状态必须合法等）
- 做一致的“找不到任务”处理（抛异常或返回 None —— 推荐抛异常）

> 重要：**不要让 CLI 直接操作 storage**。CLI 只负责解析参数/展示输出，真正的业务逻辑在 `TaskService`。

### Step 2: 设计接口与数据结构（10 分钟）

你最终希望这样使用：
```python
from src.services.task_service import TaskService
from src.storage.json_storage import JSONStorage
from src.models.task import Status, Priority

service = TaskService(JSONStorage("data/tasks.json"))

service.add_task("学习 Service 层", Priority.HIGH)
service.list_tasks()
service.update_task_status("<task_id>", Status.DONE)
service.delete_task("<task_id>")
```

这里我们建议采用 **UUID 字符串**作为 `Task.id`（因为你当前的 `Task` 并没有强制 id 类型）。

---

## 🧩 代码大纲（先写骨架，再补逻辑）

创建 `src/services/task_service.py`，先把结构搭起来：

```python
import uuid
from typing import List, Optional

from src.models.task import Task, Status, Priority
from src.storage.json_storage import JSONStorage


class TaskService:
    def __init__(self, storage: JSONStorage):
        self.storage = storage

    def add_task(self, title: str, priority: Priority = Priority.MEDIUM) -> Task:
        """1) 校验 title  2) 生成 id  3) 创建 Task  4) 追加并保存  5) 返回 Task"""
        # TODO: 校验 title
        # TODO: 生成 UUID
        # TODO: 加载 tasks
        # TODO: 创建并 append
        # TODO: save
        # TODO: return
        raise NotImplementedError

    def get_task(self, task_id: str) -> Task:
        """按 id 查找任务；找不到要给出明确错误。"""
        # TODO: load
        # TODO: 遍历查找
        # TODO: 找不到 -> raise
        raise NotImplementedError

    def list_tasks(self, status: Optional[Status] = None) -> List[Task]:
        """列出任务；如果传入 status 则过滤。"""
        # TODO: load
        # TODO: if status is None: return all
        # TODO: else: filter
        raise NotImplementedError

    def update_task_status(self, task_id: str, status: Status) -> Task:
        """更新任务状态并持久化。"""
        # TODO: load
        # TODO: 找到 task
        # TODO: task.update_status(status)
        # TODO: save
        # TODO: return task
        raise NotImplementedError

    def delete_task(self, task_id: str) -> None:
        """删除任务并持久化。"""
        # TODO: load
        # TODO: 过滤掉目标 task
        # TODO: 如果数量没变说明没找到 -> raise
        # TODO: save
        raise NotImplementedError
```

### 你填逻辑时的关键点
- `title` 建议做：`title.strip()`，空则报错
- UUID：`uuid.uuid4().hex`（短一些）或 `str(uuid.uuid4())`
- `get_task`/`update`/`delete` 找不到时：
  - 推荐：`raise ValueError(f"Task not found: {task_id}")`
- `list_tasks` 过滤建议用列表推导式：
  - `[t for t in tasks if t.status == status]`

---

## ✅ 单元测试大纲（先列测试点，再实现）

创建 `tests/test_task_service.py`（建议用 `tmp_path` 隔离文件）：

测试点建议最少覆盖：
- [ ] `add_task`:
  - 创建任务成功（返回 Task；保存后能 load 到）
  - title 为空时报错
- [ ] `get_task`:
  - 能获取存在的任务
  - 获取不存在的任务时报错
- [ ] `list_tasks`:
  - 不传 status 返回全部
  - 传 status 能正确过滤
- [ ] `update_task_status`:
  - 状态更新成功（同时 updated_at 有变化）
  - 更新不存在任务时报错
- [ ] `delete_task`:
  - 删除成功（数量减少）
  - 删除不存在任务时报错

---

## ▶️ 运行测试（10 分钟）

```bash
pytest tests/test_task_service.py -v
pytest tests/ -v
```

---

## ✅ 今日成果检查

### 文件清单
- [ ] `src/services/task_service.py`
- [ ] `tests/test_task_service.py`

### 功能验证（手动）
- [ ] 添加 3 个任务
- [ ] 列出全部任务
- [ ] 过滤出 `pending` 或 `done`
- [ ] 更新一个任务状态为 `done`
- [ ] 删除一个任务

---

## 💡 常见问题

### Q1: 为什么要多一层 Service？直接在 CLI 调 storage 不行吗？
**A**: 可以写出来，但会变得不可维护。Service 把“规则”集中在一个地方：
- 之后要加日志、异常、自定义规则时，只改 Service
- CLI / Web API / GUI 都能复用同一套业务逻辑

### Q2: UUID 有什么好处？
**A**: 不用维护计数器，不怕并发冲突，天然全局唯一。

---

## ✅ 参考实现（完整正确代码）

> 说明：下面给出 `TaskService` + `test_task_service.py` 的一份可运行参考实现。你可以先照着骨架自己写，卡住了再对照。

### 1) `src/services/task_service.py`

```python
import uuid
from typing import List, Optional

from src.models.task import Task, Status, Priority
from src.storage.json_storage import JSONStorage


class TaskService:
    def __init__(self, storage: JSONStorage):
        self.storage = storage

    def add_task(self, title: str, priority: Priority = Priority.MEDIUM) -> Task:
        if title is None:
            raise ValueError("title is required")
        cleaned = title.strip()
        if not cleaned:
            raise ValueError("title cannot be empty")

        task_id = uuid.uuid4().hex
        tasks = self.storage.load()

        task = Task(id=task_id, title=cleaned, priority=priority)
        tasks.append(task)
        self.storage.save(tasks)
        return task

    def get_task(self, task_id: str) -> Task:
        tasks = self.storage.load()
        for task in tasks:
            if str(task.id) == str(task_id):
                return task
        raise ValueError(f"Task not found: {task_id}")

    def list_tasks(self, status: Optional[Status] = None) -> List[Task]:
        tasks = self.storage.load()
        if status is None:
            return tasks
        return [t for t in tasks if t.status == status]

    def update_task_status(self, task_id: str, status: Status) -> Task:
        tasks = self.storage.load()
        for task in tasks:
            if str(task.id) == str(task_id):
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
```

### 2) `tests/test_task_service.py`

```python
import pytest

from src.models.task import Status, Priority
from src.storage.json_storage import JSONStorage
from src.services.task_service import TaskService


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

        # persisted
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
        with pytest.raises(ValueError):
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

        # persisted
        fetched = service.get_task(task.id)
        assert fetched.status == Status.DONE

    def test_update_task_status_not_found_raises(self, service):
        with pytest.raises(ValueError):
            service.update_task_status("not-exist", Status.DONE)

    def test_delete_task_success(self, service):
        t1 = service.add_task("t1")
        t2 = service.add_task("t2")

        service.delete_task(t1.id)
        tasks = service.list_tasks()
        assert len(tasks) == 1
        assert str(tasks[0].id) == str(t2.id)

        with pytest.raises(ValueError):
            service.get_task(t1.id)

    def test_delete_task_not_found_raises(self, service):
        with pytest.raises(ValueError):
            service.delete_task("not-exist")
```

---

## 📝 今日总结

在 Day 3，你完成了：
1. ✅ 把核心业务逻辑集中到 `TaskService`
2. ✅ 实现了完整的 CRUD + 状态更新
3. ✅ 引入 UUID 作为任务 ID 生成方案
4. ✅ 编写并通过 Service 层单元测试

**明天预告（Day 4）**：
- 日志系统 + 自定义异常
- 让 Service 层的错误更“可读、可追踪、可维护”
