# Day 6 Practical Guide: API Testing + Postman Collection

## 🎯 Today's Goals
- Configure pytest testing environment
- Write complete API endpoint tests
- Create test database
- Implement test coverage analysis
- Create Postman test collection

**Estimated Time**: 2-3 hours  
**Difficulty**: ⭐⭐⭐ (Intermediate)

---

## 📚 Preparation Before Starting (30 minutes)

### 1. Read Learning Materials
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [pytest Official Documentation](https://docs.pytest.org/)
- [httpx Documentation](https://www.python-httpx.org/)

### 2. Understand Testing Concepts

#### Test Types
- **Unit Tests** - Test individual functions/methods
- **Integration Tests** - Test interactions between multiple components
- **End-to-End Tests** - Test complete user flows

#### Testing Pyramid
```
       /\
      /E2E\      ← Few end-to-end tests
     /------\
    /Integration\  ← Moderate integration tests
   /----------\
  /  Unit Tests  \  ← Many unit tests
 /--------------\
```

---

## 🛠️ Practical Steps

### Step 1: Configure Test Environment (30 minutes) ⭐ Core

Create `tests/conftest.py`:

```python
"""
pytest configuration and fixtures
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.main import app
from src.database.base import Base
from src.database.connection import get_db

# Use in-memory database for testing
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
    Create test database session
    Each test function creates a new database
    """
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Drop all tables
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """
    Create test client
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
    Sample Todo data
    """
    return {
        "title": "Test Task",
        "description": "This is a test task",
        "priority": "high"
    }


@pytest.fixture
def create_sample_todo(client, sample_todo_data):
    """
    Fixture to create sample Todo
    """
    def _create_todo(data=None):
        if data is None:
            data = sample_todo_data
        response = client.post("/todos", json=data)
        return response.json()
    
    return _create_todo
```

**Code Explanation**:
1. **In-memory database** - Use SQLite in-memory database for fast and isolated testing
2. **scope="function"** - Each test function has an independent database
3. **fixture** - pytest's dependency injection mechanism
4. **TestClient** - Test client provided by FastAPI

### Step 2: Write API Endpoint Tests (60 minutes) ⭐ Core

Create `tests/test_todos_api.py`:

```python
"""
Todo API endpoint tests
"""
import pytest
from fastapi import status


class TestCreateTodo:
    """Test creating Todo"""
    
    def test_create_todo_success(self, client, sample_todo_data):
        """Test successful Todo creation"""
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
        """Test creating Todo without title"""
        response = client.post("/todos", json={
            "description": "Test",
            "priority": "high"
        })
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_todo_with_empty_title(self, client):
        """Test creating Todo with empty title"""
        response = client.post("/todos", json={
            "title": "",
            "priority": "high"
        })
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_todo_with_invalid_priority(self, client):
        """Test creating Todo with invalid priority"""
        response = client.post("/todos", json={
            "title": "Test",
            "priority": "urgent"  # Invalid priority
        })
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_todo_with_long_title(self, client):
        """Test creating Todo with too long title"""
        response = client.post("/todos", json={
            "title": "a" * 201,  # Over 200 characters
            "priority": "high"
        })
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestGetTodos:
    """Test getting Todo list"""
    
    def test_get_empty_todos(self, client):
        """Test getting empty Todo list"""
        response = client.get("/todos")
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["todos"] == []
        assert data["total"] == 0
    
    def test_get_todos_with_data(self, client, create_sample_todo):
        """Test getting Todo list with data"""
        # Create 3 Todos
        create_sample_todo()
        create_sample_todo()
        create_sample_todo()
        
        response = client.get("/todos")
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert len(data["todos"]) == 3
        assert data["total"] == 3
    
    def test_get_todos_with_status_filter(self, client, create_sample_todo):
        """Test filtering Todos by status"""
        # Create and update a Todo
        todo = create_sample_todo()
        client.put(f"/todos/{todo['id']}", json={"status": "done"})
        
        # Create another Todo
        create_sample_todo()
        
        # Filter completed Todos
        response = client.get("/todos?status=done")
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["total"] == 1
        assert data["todos"][0]["status"] == "done"
    
    def test_get_todos_with_pagination(self, client, create_sample_todo):
        """Test pagination"""
        # Create 15 Todos
        for _ in range(15):
            create_sample_todo()
        
        # Get page 1 (10 items per page)
        response = client.get("/todos?page=1&page_size=10")
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert len(data["todos"]) == 10
        assert data["total"] == 15
        assert data["page"] == 1
        assert data["total_pages"] == 2
    
    def test_get_todos_with_search(self, client, create_sample_todo):
        """Test search functionality"""
        # Create Todos with specific titles
        client.post("/todos", json={
            "title": "Learn Python",
            "priority": "high"
        })
        client.post("/todos", json={
            "title": "Learn FastAPI",
            "priority": "high"
        })
        
        # Search for Todos containing "Python"
        response = client.get("/todos?search=Python")
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["total"] == 1
        assert "Python" in data["todos"][0]["title"]


class TestGetTodo:
    """Test getting single Todo"""
    
    def test_get_existing_todo(self, client, create_sample_todo):
        """Test getting existing Todo"""
        todo = create_sample_todo()
        
        response = client.get(f"/todos/{todo['id']}")
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["id"] == todo["id"]
        assert data["title"] == todo["title"]
    
    def test_get_nonexistent_todo(self, client):
        """Test getting non-existent Todo"""
        response = client.get("/todos/999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestUpdateTodo:
    """Test updating Todo"""
    
    def test_update_todo_title(self, client, create_sample_todo):
        """Test updating Todo title"""
        todo = create_sample_todo()
        
        response = client.put(f"/todos/{todo['id']}", json={
            "title": "New Title"
        })
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["title"] == "New Title"
    
    def test_update_todo_status(self, client, create_sample_todo):
        """Test updating Todo status"""
        todo = create_sample_todo()
        
        response = client.put(f"/todos/{todo['id']}", json={
            "status": "done"
        })
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["status"] == "done"
    
    def test_update_nonexistent_todo(self, client):
        """Test updating non-existent Todo"""
        response = client.put("/todos/999", json={
            "title": "New Title"
        })
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestDeleteTodo:
    """Test deleting Todo"""
    
    def test_delete_existing_todo(self, client, create_sample_todo):
        """Test deleting existing Todo"""
        todo = create_sample_todo()
        
        response = client.delete(f"/todos/{todo['id']}")
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify deletion
        get_response = client.get(f"/todos/{todo['id']}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_nonexistent_todo(self, client):
        """Test deleting non-existent Todo"""
        response = client.delete("/todos/999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestTodoStats:
    """Test Todo statistics"""
    
    def test_get_stats(self, client, create_sample_todo):
        """Test getting statistics"""
        # Create Todos with different statuses and priorities
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

### Step 3: Run Tests (20 minutes)

```bash
# 1. Run all tests
pytest tests/ -v

# 2. Run specific test file
pytest tests/test_todos_api.py -v

# 3. Run specific test class
pytest tests/test_todos_api.py::TestCreateTodo -v

# 4. Run specific test method
pytest tests/test_todos_api.py::TestCreateTodo::test_create_todo_success -v

# 5. View test coverage
pytest tests/ --cov=src --cov-report=html

# 6. View detailed coverage report
open htmlcov/index.html  # macOS
```

### Step 4: Create Postman Test Collection (30 minutes)

Create `docs/postman_collection.json`:

```json
{
  "info": {
    "name": "FastAPI TODO API",
    "description": "Complete TODO API test collection",
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
          "raw": "{\n  \"title\": \"Learn FastAPI\",\n  \"description\": \"Complete FastAPI tutorial\",\n  \"priority\": \"high\"\n}"
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

## ✅ Today's Results Checklist

### File List
- [x] `tests/conftest.py` - pytest configuration
- [x] `tests/test_todos_api.py` - API tests
- [x] `docs/postman_collection.json` - Postman collection

### Function Verification
```bash
# 1. Run all tests
pytest tests/ -v

# 2. View coverage
pytest tests/ --cov=src --cov-report=term-missing

# 3. Import Postman collection
# Open Postman → Import → Select postman_collection.json
```

### Learning Achievements
- [x] Mastered pytest testing framework
- [x] Learned to write API tests
- [x] Understood test coverage
- [x] Learned to use Postman
- [x] Mastered testing best practices

---

## 📝 Today's Summary

On Day 6, you completed:
1. ✅ Configured test environment
2. ✅ Wrote complete API tests
3. ✅ Implemented test coverage analysis
4. ✅ Created Postman test collection
5. ✅ Mastered testing best practices

**Tomorrow's Preview (Day 7)**:
- Improve project documentation
- Optimize code structure
- Prepare for deployment
- Project summary

---

**Congratulations on completing Day 6! Testing coverage complete!** 🎉
