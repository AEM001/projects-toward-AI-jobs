# Day 6 实战指南：API 测试 + Postman 集合

## 🎯 今日目标
- 配置 pytest 测试环境
- 编写完整的 API 端点测试
- 创建测试数据库
- 实现测试覆盖率分析
- 创建 Postman 测试集合

**预计时间**: 2-3 小时  
**难度**: ⭐⭐⭐ (中级)

---

## 📚 开始前的准备（30 分钟）

### 1. 阅读学习资料
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [pytest 官方文档](https://docs.pytest.org/)
- [httpx 文档](https://www.python-httpx.org/)

### 2. 理解测试概念

#### 测试类型
- **单元测试** - 测试单个函数/方法
- **集成测试** - 测试多个组件的交互
- **端到端测试** - 测试完整的用户流程

#### 测试金字塔
```
       /\
      /E2E\      ← 少量端到端测试
     /------\
    /集成测试\    ← 适量集成测试
   /----------\
  /  单元测试  \  ← 大量单元测试
 /--------------\
```

---

## 🛠️ 实战步骤

### Step 1: 配置测试环境（30 分钟）⭐ 核心

创建 `tests/conftest.py`：

```python
"""
pytest 配置和 fixtures
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.main import app
from src.database.base import Base
from src.database.connection import get_db

# 使用内存数据库进行测试
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """
    创建测试数据库会话
    每个测试函数都会创建新的数据库
    """
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    
    # 创建会话
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # 删除所有表
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """
    创建测试客户端
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_todo_data():
    """
    示例 Todo 数据
    """
    return {
        "title": "测试任务",
        "description": "这是一个测试任务",
        "priority": "high"
    }


@pytest.fixture
def create_sample_todo(client, sample_todo_data):
    """
    创建示例 Todo 的 fixture
    """
    def _create_todo(data=None):
        if data is None:
            data = sample_todo_data
        response = client.post("/todos", json=data)
        return response.json()
    
    return _create_todo
```

**代码讲解**：
1. **内存数据库** - 使用 SQLite 内存数据库，测试快速且隔离
2. **scope="function"** - 每个测试函数都有独立的数据库
3. **fixture** - pytest 的依赖注入机制
4. **TestClient** - FastAPI 提供的测试客户端

### Step 2: 编写 API 端点测试（60 分钟）⭐ 核心

创建 `tests/test_todos_api.py`：

```python
"""
Todo API 端点测试
"""
import pytest
from fastapi import status


class TestCreateTodo:
    """测试创建 Todo"""
    
    def test_create_todo_success(self, client, sample_todo_data):
        """测试成功创建 Todo"""
        response = client.post("/todos", json=sample_todo_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        assert data["title"] == sample_todo_data["title"]
        assert data["description"] == sample_todo_data["description"]
        assert data["priority"] == sample_todo_data["priority"]
        assert data["status"] == "pending"
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_create_todo_without_title(self, client):
        """测试创建 Todo 时缺少标题"""
        response = client.post("/todos", json={
            "description": "测试",
            "priority": "high"
        })
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_todo_with_empty_title(self, client):
        """测试创建 Todo 时标题为空"""
        response = client.post("/todos", json={
            "title": "",
            "priority": "high"
        })
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_todo_with_invalid_priority(self, client):
        """测试创建 Todo 时优先级无效"""
        response = client.post("/todos", json={
            "title": "测试",
            "priority": "urgent"  # 无效的优先级
        })
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_todo_with_long_title(self, client):
        """测试创建 Todo 时标题过长"""
        response = client.post("/todos", json={
            "title": "a" * 201,  # 超过 200 字符
            "priority": "high"
        })
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestGetTodos:
    """测试获取 Todo 列表"""
    
    def test_get_empty_todos(self, client):
        """测试获取空的 Todo 列表"""
        response = client.get("/todos")
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["todos"] == []
        assert data["total"] == 0
    
    def test_get_todos_with_data(self, client, create_sample_todo):
        """测试获取有数据的 Todo 列表"""
        # 创建 3 个 Todo
        create_sample_todo()
        create_sample_todo()
        create_sample_todo()
        
        response = client.get("/todos")
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert len(data["todos"]) == 3
        assert data["total"] == 3
    
    def test_get_todos_with_status_filter(self, client, create_sample_todo):
        """测试按状态筛选 Todo"""
        # 创建并更新一个 Todo
        todo = create_sample_todo()
        client.put(f"/todos/{todo['id']}", json={"status": "done"})
        
        # 创建另一个 Todo
        create_sample_todo()
        
        # 筛选已完成的 Todo
        response = client.get("/todos?status=done")
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["total"] == 1
        assert data["todos"][0]["status"] == "done"
    
    def test_get_todos_with_pagination(self, client, create_sample_todo):
        """测试分页"""
        # 创建 15 个 Todo
        for _ in range(15):
            create_sample_todo()
        
        # 获取第 1 页（每页 10 条）
        response = client.get("/todos?page=1&page_size=10")
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert len(data["todos"]) == 10
        assert data["total"] == 15
        assert data["page"] == 1
        assert data["total_pages"] == 2
    
    def test_get_todos_with_search(self, client, create_sample_todo):
        """测试搜索功能"""
        # 创建特定标题的 Todo
        client.post("/todos", json={
            "title": "学习 Python",
            "priority": "high"
        })
        client.post("/todos", json={
            "title": "学习 FastAPI",
            "priority": "high"
        })
        
        # 搜索包含 "Python" 的 Todo
        response = client.get("/todos?search=Python")
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["total"] == 1
        assert "Python" in data["todos"][0]["title"]


class TestGetTodo:
    """测试获取单个 Todo"""
    
    def test_get_existing_todo(self, client, create_sample_todo):
        """测试获取存在的 Todo"""
        todo = create_sample_todo()
        
        response = client.get(f"/todos/{todo['id']}")
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["id"] == todo["id"]
        assert data["title"] == todo["title"]
    
    def test_get_nonexistent_todo(self, client):
        """测试获取不存在的 Todo"""
        response = client.get("/todos/999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestUpdateTodo:
    """测试更新 Todo"""
    
    def test_update_todo_title(self, client, create_sample_todo):
        """测试更新 Todo 标题"""
        todo = create_sample_todo()
        
        response = client.put(f"/todos/{todo['id']}", json={
            "title": "新标题"
        })
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["title"] == "新标题"
    
    def test_update_todo_status(self, client, create_sample_todo):
        """测试更新 Todo 状态"""
        todo = create_sample_todo()
        
        response = client.put(f"/todos/{todo['id']}", json={
            "status": "done"
        })
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["status"] == "done"
    
    def test_update_nonexistent_todo(self, client):
        """测试更新不存在的 Todo"""
        response = client.put("/todos/999", json={
            "title": "新标题"
        })
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestDeleteTodo:
    """测试删除 Todo"""
    
    def test_delete_existing_todo(self, client, create_sample_todo):
        """测试删除存在的 Todo"""
        todo = create_sample_todo()
        
        response = client.delete(f"/todos/{todo['id']}")
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # 验证已删除
        get_response = client.get(f"/todos/{todo['id']}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_nonexistent_todo(self, client):
        """测试删除不存在的 Todo"""
        response = client.delete("/todos/999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestTodoStats:
    """测试 Todo 统计"""
    
    def test_get_stats(self, client, create_sample_todo):
        """测试获取统计信息"""
        # 创建不同状态和优先级的 Todo
        todo1 = create_sample_todo()
        todo2 = create_sample_todo()
        
        client.put(f"/todos/{todo1['id']}", json={"status": "done"})
        
        response = client.get("/todos/stats")
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["total"] == 2
        assert data["done"] == 1
        assert data["pending"] == 1
```

### Step 3: 运行测试（20 分钟）

```bash
# 1. 运行所有测试
pytest tests/ -v

# 2. 运行特定测试文件
pytest tests/test_todos_api.py -v

# 3. 运行特定测试类
pytest tests/test_todos_api.py::TestCreateTodo -v

# 4. 运行特定测试方法
pytest tests/test_todos_api.py::TestCreateTodo::test_create_todo_success -v

# 5. 查看测试覆盖率
pytest tests/ --cov=src --cov-report=html

# 6. 查看详细的覆盖率报告
open htmlcov/index.html  # macOS
```

### Step 4: 创建 Postman 测试集合（30 分钟）

创建 `docs/postman_collection.json`：

```json
{
  "info": {
    "name": "FastAPI TODO API",
    "description": "完整的 TODO API 测试集合",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:8000",
      "type": "string"
    },
    {
      "key": "todo_id",
      "value": "",
      "type": "string"
    }
  ],
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "{{base_url}}/health",
          "host": ["{{base_url}}"],
          "path": ["health"]
        }
      }
    },
    {
      "name": "Create Todo",
      "event": [
        {
          "listen": "test",
          "script": {
            "exec": [
              "pm.test('Status code is 201', function () {",
              "    pm.response.to.have.status(201);",
              "});",
              "",
              "pm.test('Response has id', function () {",
              "    var jsonData = pm.response.json();",
              "    pm.expect(jsonData).to.have.property('id');",
              "    pm.collectionVariables.set('todo_id', jsonData.id);",
              "});"
            ]
          }
        }
      ],
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"title\": \"学习 FastAPI\",\n  \"description\": \"完成 FastAPI 教程\",\n  \"priority\": \"high\"\n}"
        },
        "url": {
          "raw": "{{base_url}}/todos",
          "host": ["{{base_url}}"],
          "path": ["todos"]
        }
      }
    },
    {
      "name": "Get All Todos",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "{{base_url}}/todos",
          "host": ["{{base_url}}"],
          "path": ["todos"]
        }
      }
    },
    {
      "name": "Get Todo by ID",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "{{base_url}}/todos/{{todo_id}}",
          "host": ["{{base_url}}"],
          "path": ["todos", "{{todo_id}}"]
        }
      }
    },
    {
      "name": "Update Todo",
      "request": {
        "method": "PUT",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"status\": \"done\"\n}"
        },
        "url": {
          "raw": "{{base_url}}/todos/{{todo_id}}",
          "host": ["{{base_url}}"],
          "path": ["todos", "{{todo_id}}"]
        }
      }
    },
    {
      "name": "Delete Todo",
      "request": {
        "method": "DELETE",
        "header": [],
        "url": {
          "raw": "{{base_url}}/todos/{{todo_id}}",
          "host": ["{{base_url}}"],
          "path": ["todos", "{{todo_id}}"]
        }
      }
    },
    {
      "name": "Get Stats",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "{{base_url}}/todos/stats",
          "host": ["{{base_url}}"],
          "path": ["todos", "stats"]
        }
      }
    }
  ]
}
```

---

## ✅ 今日成果检查

### 文件清单
- [x] `tests/conftest.py` - pytest 配置
- [x] `tests/test_todos_api.py` - API 测试
- [x] `docs/postman_collection.json` - Postman 集合

### 功能验证
```bash
# 1. 运行所有测试
pytest tests/ -v

# 2. 查看覆盖率
pytest tests/ --cov=src --cov-report=term-missing

# 3. 导入 Postman 集合
# 打开 Postman → Import → 选择 postman_collection.json
```

### 学习收获
- [x] 掌握 pytest 测试框架
- [x] 学会编写 API 测试
- [x] 理解测试覆盖率
- [x] 学会使用 Postman
- [x] 掌握测试最佳实践

---

## 📝 今日总结

在 Day 6，你完成了：
1. ✅ 配置了测试环境
2. ✅ 编写了完整的 API 测试
3. ✅ 实现了测试覆盖率分析
4. ✅ 创建了 Postman 测试集合
5. ✅ 掌握了测试最佳实践

**明天预告（Day 7）**：
- 完善项目文档
- 优化代码结构
- 准备部署
- 项目总结

---

**恭喜完成 Day 6！测试覆盖完成！** 🎉
