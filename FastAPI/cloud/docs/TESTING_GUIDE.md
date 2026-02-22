# FastAPI Testing Guide - Week 3

This comprehensive guide will help you implement a complete testing suite for your FastAPI Todo application with authentication.

---

## **Overview**

You'll be testing three layers of your application:
1. **CRUD Layer** (`crud.py`) - Database operations
2. **Service Layer** (`services.py`) - Business logic
3. **API Layer** (`main.py`) - HTTP endpoints

---

## **Day 1-2: Setup Testing Framework (3-4 hours)**

### **Step 1: Install Testing Dependencies**

```bash
pip install pytest pytest-cov httpx pytest-asyncio
```

**What each package does:**
- `pytest`: Testing framework with powerful fixtures and assertions
- `pytest-cov`: Code coverage reporting
- `httpx`: Async HTTP client for testing FastAPI endpoints
- `pytest-asyncio`: Support for async test functions

### **Step 2: Create Test Directory Structure**

```bash
mkdir tests
touch tests/__init__.py
touch tests/conftest.py
touch tests/test_crud.py
touch tests/test_services.py
touch tests/test_api.py
```

**Directory structure:**
```
FastAPI/
├── main.py
├── crud.py
├── services.py
├── db.py
├── schemas.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Shared fixtures
│   ├── test_crud.py         # CRUD layer tests
│   ├── test_services.py     # Service layer tests
│   └── test_api.py          # API endpoint tests
```

### **Step 3: Create Test Database Configuration**

**File: `tests/conftest.py`**

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from db import Base, TodoDB, UserDB
from main import app, get_db, get_current_user
from schemas import User
import os

# Use in-memory SQLite for tests
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_test.db"

@pytest.fixture(scope="function")
def test_db():
    """Create a fresh test database for each test"""
    # Create test engine
    engine = create_engine(
        SQLALCHEMY_TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=engine)
        # Remove test database file
        if os.path.exists("./test_test.db"):
            os.remove("./test_test.db")

@pytest.fixture(scope="function")
def client(test_db):
    """Create a test client with overridden database dependency"""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def test_user(test_db):
    """Create a test user in the database"""
    from main import get_password_hash
    
    user = UserDB(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword123")
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user

@pytest.fixture(scope="function")
def auth_client(client, test_user):
    """Create an authenticated test client"""
    # Login to get token
    response = client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "testpassword123"}
    )
    token = response.json()["access_token"]
    
    # Add authorization header to client
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    return client

@pytest.fixture(scope="function")
def sample_todo(test_db, test_user):
    """Create a sample todo for testing"""
    from datetime import datetime, timedelta
    
    todo = TodoDB(
        title="Test Todo",
        ddl=datetime.now() + timedelta(days=1),
        done=False,
        owner_id=test_user.id
    )
    test_db.add(todo)
    test_db.commit()
    test_db.refresh(todo)
    return todo
```

**Key concepts in conftest.py:**
- **`scope="function"`**: Creates a fresh fixture for each test (isolation)
- **`test_db` fixture**: Provides a clean database for each test
- **`client` fixture**: FastAPI test client with database override
- **`test_user` fixture**: Pre-created user for authentication tests
- **`auth_client` fixture**: Authenticated client with JWT token
- **`sample_todo` fixture**: Pre-created todo for update/delete tests

---

## **Day 3-5: Write Unit Tests (5-6 hours)**

### **Part 1: Test CRUD Functions**

**File: `tests/test_crud.py`**

```python
import pytest
from datetime import datetime, timedelta
from crud import (
    create_todo, list_todos, get_todo, 
    update_todo, delete_todo, format_datetime
)
from schemas import TodoCreate, TodoUpdate
from db import TodoDB

class TestFormatDatetime:
    """Test datetime formatting utility"""
    
    def test_format_datetime_with_value(self):
        dt = datetime(2026, 2, 15, 14, 30, 45)
        result = format_datetime(dt)
        assert result == "2026-02-15 14:30"
    
    def test_format_datetime_with_none(self):
        result = format_datetime(None)
        assert result is None

class TestCreateTodo:
    """Test todo creation in CRUD layer"""
    
    def test_create_todo_with_ddl(self, test_db, test_user):
        """Test creating a todo with a deadline"""
        todo_data = TodoCreate(
            title="Buy groceries",
            ddl="2026-02-20 18:00"
        )
        
        result = create_todo(test_db, todo_data, test_user.id)
        
        assert result.id is not None
        assert result.title == "Buy groceries"
        assert result.done is False
        assert result.owner_id == test_user.id
        assert result.ddl is not None
    
    def test_create_todo_without_ddl(self, test_db, test_user):
        """Test creating a todo without deadline (uses default)"""
        todo_data = TodoCreate(title="Read book", ddl=None)
        
        result = create_todo(test_db, todo_data, test_user.id)
        
        assert result.id is not None
        assert result.title == "Read book"
        assert result.ddl is not None  # Should have default value
    
    def test_create_todo_with_invalid_ddl_format(self, test_db, test_user):
        """Test creating todo with invalid date format falls back to default"""
        todo_data = TodoCreate(title="Invalid date", ddl="invalid-date")
        
        result = create_todo(test_db, todo_data, test_user.id)
        
        assert result.id is not None
        assert result.ddl is not None  # Should use default

class TestListTodos:
    """Test listing todos with filters and pagination"""
    
    def test_list_todos_empty(self, test_db, test_user):
        """Test listing when no todos exist"""
        todos, total = list_todos(test_db, test_user.id)
        
        assert todos == []
        assert total == 0
    
    def test_list_todos_with_data(self, test_db, test_user):
        """Test listing todos for a user"""
        # Create test todos
        todo1 = TodoDB(title="Todo 1", owner_id=test_user.id, done=False)
        todo2 = TodoDB(title="Todo 2", owner_id=test_user.id, done=True)
        test_db.add_all([todo1, todo2])
        test_db.commit()
        
        todos, total = list_todos(test_db, test_user.id)
        
        assert len(todos) == 2
        assert total == 2
    
    def test_list_todos_pagination(self, test_db, test_user):
        """Test pagination works correctly"""
        # Create 5 todos
        for i in range(5):
            todo = TodoDB(title=f"Todo {i}", owner_id=test_user.id)
            test_db.add(todo)
        test_db.commit()
        
        # Get first page (2 items)
        todos, total = list_todos(test_db, test_user.id, skip=0, limit=2)
        assert len(todos) == 2
        assert total == 5
        
        # Get second page
        todos, total = list_todos(test_db, test_user.id, skip=2, limit=2)
        assert len(todos) == 2
        assert total == 5
    
    def test_list_todos_title_filter(self, test_db, test_user):
        """Test filtering by title"""
        todo1 = TodoDB(title="Buy groceries", owner_id=test_user.id)
        todo2 = TodoDB(title="Read book", owner_id=test_user.id)
        test_db.add_all([todo1, todo2])
        test_db.commit()
        
        todos, total = list_todos(test_db, test_user.id, title="groceries")
        
        assert len(todos) == 1
        assert todos[0].title == "Buy groceries"
    
    def test_list_todos_sorting(self, test_db, test_user):
        """Test sorting by different fields"""
        todo1 = TodoDB(title="B Task", owner_id=test_user.id)
        todo2 = TodoDB(title="A Task", owner_id=test_user.id)
        test_db.add_all([todo1, todo2])
        test_db.commit()
        
        # Sort by title ascending
        todos, _ = list_todos(test_db, test_user.id, sort_by="title", sort_order="asc")
        assert todos[0].title == "A Task"
        assert todos[1].title == "B Task"
        
        # Sort by title descending
        todos, _ = list_todos(test_db, test_user.id, sort_by="title", sort_order="desc")
        assert todos[0].title == "B Task"
        assert todos[1].title == "A Task"
    
    def test_list_todos_user_isolation(self, test_db, test_user):
        """Test that users only see their own todos"""
        # Create another user
        from main import get_password_hash
        from db import UserDB
        
        other_user = UserDB(
            email="other@example.com",
            hashed_password=get_password_hash("password")
        )
        test_db.add(other_user)
        test_db.commit()
        test_db.refresh(other_user)
        
        # Create todos for both users
        todo1 = TodoDB(title="User 1 Todo", owner_id=test_user.id)
        todo2 = TodoDB(title="User 2 Todo", owner_id=other_user.id)
        test_db.add_all([todo1, todo2])
        test_db.commit()
        
        # Each user should only see their own todos
        user1_todos, _ = list_todos(test_db, test_user.id)
        assert len(user1_todos) == 1
        assert user1_todos[0].title == "User 1 Todo"
        
        user2_todos, _ = list_todos(test_db, other_user.id)
        assert len(user2_todos) == 1
        assert user2_todos[0].title == "User 2 Todo"

class TestGetTodo:
    """Test getting a single todo"""
    
    def test_get_todo_success(self, test_db, test_user, sample_todo):
        """Test getting an existing todo"""
        result = get_todo(test_db, sample_todo.id, test_user.id)
        
        assert result is not None
        assert result.id == sample_todo.id
        assert result.title == sample_todo.title
    
    def test_get_todo_not_found(self, test_db, test_user):
        """Test getting a non-existent todo returns None"""
        result = get_todo(test_db, 99999, test_user.id)
        
        assert result is None
    
    def test_get_todo_wrong_owner(self, test_db, test_user, sample_todo):
        """Test that users can't access other users' todos"""
        from main import get_password_hash
        from db import UserDB
        
        other_user = UserDB(
            email="other@example.com",
            hashed_password=get_password_hash("password")
        )
        test_db.add(other_user)
        test_db.commit()
        test_db.refresh(other_user)
        
        # Try to get test_user's todo as other_user
        result = get_todo(test_db, sample_todo.id, other_user.id)
        
        assert result is None

class TestUpdateTodo:
    """Test updating todos"""
    
    def test_update_todo_title(self, test_db, test_user, sample_todo):
        """Test updating todo title"""
        update_data = TodoUpdate(title="Updated Title")
        
        result = update_todo(test_db, sample_todo.id, test_user.id, update_data)
        
        assert result is not None
        assert result.title == "Updated Title"
        assert result.done == sample_todo.done  # Unchanged
    
    def test_update_todo_done_status(self, test_db, test_user, sample_todo):
        """Test updating todo completion status"""
        update_data = TodoUpdate(done=True)
        
        result = update_todo(test_db, sample_todo.id, test_user.id, update_data)
        
        assert result is not None
        assert result.done is True
    
    def test_update_todo_ddl(self, test_db, test_user, sample_todo):
        """Test updating todo deadline"""
        update_data = TodoUpdate(ddl="2026-03-01 10:00")
        
        result = update_todo(test_db, sample_todo.id, test_user.id, update_data)
        
        assert result is not None
        assert result.ddl is not None
    
    def test_update_todo_clear_ddl(self, test_db, test_user, sample_todo):
        """Test clearing todo deadline"""
        update_data = TodoUpdate(ddl="")
        
        result = update_todo(test_db, sample_todo.id, test_user.id, update_data)
        
        assert result is not None
        assert result.ddl is None
    
    def test_update_todo_not_found(self, test_db, test_user):
        """Test updating non-existent todo returns None"""
        update_data = TodoUpdate(title="New Title")
        
        result = update_todo(test_db, 99999, test_user.id, update_data)
        
        assert result is None
    
    def test_update_todo_wrong_owner(self, test_db, test_user, sample_todo):
        """Test users can't update other users' todos"""
        from main import get_password_hash
        from db import UserDB
        
        other_user = UserDB(
            email="other@example.com",
            hashed_password=get_password_hash("password")
        )
        test_db.add(other_user)
        test_db.commit()
        test_db.refresh(other_user)
        
        update_data = TodoUpdate(title="Hacked")
        result = update_todo(test_db, sample_todo.id, other_user.id, update_data)
        
        assert result is None

class TestDeleteTodo:
    """Test deleting todos"""
    
    def test_delete_todo_success(self, test_db, test_user, sample_todo):
        """Test deleting an existing todo"""
        result = delete_todo(test_db, sample_todo.id, test_user.id)
        
        assert result is True
        
        # Verify it's actually deleted
        deleted = get_todo(test_db, sample_todo.id, test_user.id)
        assert deleted is None
    
    def test_delete_todo_not_found(self, test_db, test_user):
        """Test deleting non-existent todo returns False"""
        result = delete_todo(test_db, 99999, test_user.id)
        
        assert result is False
    
    def test_delete_todo_wrong_owner(self, test_db, test_user, sample_todo):
        """Test users can't delete other users' todos"""
        from main import get_password_hash
        from db import UserDB
        
        other_user = UserDB(
            email="other@example.com",
            hashed_password=get_password_hash("password")
        )
        test_db.add(other_user)
        test_db.commit()
        test_db.refresh(other_user)
        
        result = delete_todo(test_db, sample_todo.id, other_user.id)
        
        assert result is False
        
        # Verify todo still exists
        still_exists = get_todo(test_db, sample_todo.id, test_user.id)
        assert still_exists is not None
```

**Run CRUD tests:**
```bash
pytest tests/test_crud.py -v
```

---

### **Part 2: Test Service Layer**

**File: `tests/test_services.py`**

```python
import pytest
from services import (
    create_todo_service, list_todos_service, get_todo_service,
    update_todo_service, delete_todo_service
)
from schemas import TodoCreate, TodoUpdate
from exceptions import TodoNotFoundException, DatabaseException
from db import TodoDB

class TestCreateTodoService:
    """Test todo creation service"""
    
    def test_create_todo_service_success(self, test_db, test_user):
        """Test creating a todo through service layer"""
        todo_data = TodoCreate(title="Service Test", ddl="2026-02-20 15:00")
        
        result = create_todo_service(test_db, todo_data, test_user.id)
        
        assert result.id is not None
        assert result.title == "Service Test"
        assert result.ddl == "2026-02-20 15:00"  # Formatted
        assert result.owner_id == test_user.id

class TestListTodosService:
    """Test listing todos service"""
    
    def test_list_todos_service_empty(self, test_db, test_user):
        """Test listing when no todos exist"""
        result = list_todos_service(test_db, test_user.id)
        
        assert result.items == []
        assert result.total == 0
        assert result.page == 0
        assert result.pages == 1
    
    def test_list_todos_service_with_data(self, test_db, test_user):
        """Test listing todos with pagination metadata"""
        # Create test todos
        for i in range(15):
            todo = TodoDB(title=f"Todo {i}", owner_id=test_user.id)
            test_db.add(todo)
        test_db.commit()
        
        result = list_todos_service(test_db, test_user.id, skip=0, limit=10)
        
        assert len(result.items) == 10
        assert result.total == 15
        assert result.page == 0
        assert result.pages == 2
        assert result.skip == 0
        assert result.limit == 10

class TestGetTodoService:
    """Test getting a single todo service"""
    
    def test_get_todo_service_success(self, test_db, test_user, sample_todo):
        """Test getting an existing todo"""
        result = get_todo_service(test_db, sample_todo.id, test_user.id)
        
        assert result.id == sample_todo.id
        assert result.title == sample_todo.title
    
    def test_get_todo_service_not_found(self, test_db, test_user):
        """Test getting non-existent todo raises exception"""
        with pytest.raises(TodoNotFoundException) as exc_info:
            get_todo_service(test_db, 99999, test_user.id)
        
        assert exc_info.value.todo_id == 99999

class TestUpdateTodoService:
    """Test updating todo service"""
    
    def test_update_todo_service_success(self, test_db, test_user, sample_todo):
        """Test updating a todo"""
        update_data = TodoUpdate(title="Updated via Service", done=True)
        
        result = update_todo_service(test_db, sample_todo.id, update_data, test_user.id)
        
        assert result.title == "Updated via Service"
        assert result.done is True
    
    def test_update_todo_service_not_found(self, test_db, test_user):
        """Test updating non-existent todo raises exception"""
        update_data = TodoUpdate(title="New Title")
        
        with pytest.raises(TodoNotFoundException):
            update_todo_service(test_db, 99999, update_data, test_user.id)

class TestDeleteTodoService:
    """Test deleting todo service"""
    
    def test_delete_todo_service_success(self, test_db, test_user, sample_todo):
        """Test deleting a todo"""
        # Should not raise exception
        delete_todo_service(test_db, sample_todo.id, test_user.id)
        
        # Verify it's deleted
        with pytest.raises(TodoNotFoundException):
            get_todo_service(test_db, sample_todo.id, test_user.id)
    
    def test_delete_todo_service_not_found(self, test_db, test_user):
        """Test deleting non-existent todo raises exception"""
        with pytest.raises(TodoNotFoundException):
            delete_todo_service(test_db, 99999, test_user.id)
```

**Run service tests:**
```bash
pytest tests/test_services.py -v
```

---

## **Day 6-7: Integration Tests (4-5 hours)**

### **Test API Endpoints**

**File: `tests/test_api.py`**

```python
import pytest
from fastapi import status

class TestAuthEndpoints:
    """Test authentication endpoints"""
    
    def test_register_success(self, client):
        """Test user registration"""
        response = client.post(
            "/auth/register",
            json={"email": "newuser@example.com", "password": "password123"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert "id" in data
    
    def test_register_duplicate_email(self, client, test_user):
        """Test registering with existing email fails"""
        response = client.post(
            "/auth/register",
            json={"email": "test@example.com", "password": "password123"}
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_login_success(self, client, test_user):
        """Test successful login"""
        response = client.post(
            "/auth/login",
            json={"email": "test@example.com", "password": "testpassword123"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_wrong_password(self, client, test_user):
        """Test login with wrong password"""
        response = client.post(
            "/auth/login",
            json={"email": "test@example.com", "password": "wrongpassword"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_current_user(self, auth_client, test_user):
        """Test getting current user info"""
        response = auth_client.get("/auth/me")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["id"] == test_user.id

class TestCreateTodoEndpoint:
    """Test POST /todos endpoint"""
    
    def test_create_todo_success(self, auth_client):
        """Test creating a todo"""
        response = auth_client.post(
            "/todos",
            json={"title": "API Test Todo", "ddl": "2026-02-20 18:00"}
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == "API Test Todo"
        assert data["ddl"] == "2026-02-20 18:00"
        assert data["done"] is False
        assert "id" in data
    
    def test_create_todo_without_auth(self, client):
        """Test creating todo without authentication fails"""
        response = client.post(
            "/todos",
            json={"title": "Unauthorized Todo"}
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_create_todo_validation_error(self, auth_client):
        """Test creating todo with invalid data"""
        response = auth_client.post(
            "/todos",
            json={"title": ""}  # Empty title should fail
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

class TestListTodosEndpoint:
    """Test GET /todos endpoint"""
    
    def test_list_todos_empty(self, auth_client):
        """Test listing when no todos exist"""
        response = auth_client.get("/todos")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0
    
    def test_list_todos_with_data(self, auth_client, test_db, test_user):
        """Test listing todos"""
        from db import TodoDB
        
        # Create test todos
        todo1 = TodoDB(title="Todo 1", owner_id=test_user.id)
        todo2 = TodoDB(title="Todo 2", owner_id=test_user.id)
        test_db.add_all([todo1, todo2])
        test_db.commit()
        
        response = auth_client.get("/todos")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 2
    
    def test_list_todos_pagination(self, auth_client, test_db, test_user):
        """Test pagination parameters"""
        from db import TodoDB
        
        # Create 5 todos
        for i in range(5):
            todo = TodoDB(title=f"Todo {i}", owner_id=test_user.id)
            test_db.add(todo)
        test_db.commit()
        
        response = auth_client.get("/todos?skip=0&limit=2")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 5
        assert data["page"] == 0
        assert data["pages"] == 3
    
    def test_list_todos_without_auth(self, client):
        """Test listing todos without authentication"""
        response = client.get("/todos")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

class TestGetTodoEndpoint:
    """Test GET /todos/{id} endpoint"""
    
    def test_get_todo_success(self, auth_client, sample_todo):
        """Test getting an existing todo"""
        response = auth_client.get(f"/todos/{sample_todo.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == sample_todo.id
        assert data["title"] == sample_todo.title
    
    def test_get_todo_not_found(self, auth_client):
        """Test getting non-existent todo"""
        response = auth_client.get("/todos/99999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_todo_without_auth(self, client, sample_todo):
        """Test getting todo without authentication"""
        response = client.get(f"/todos/{sample_todo.id}")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

class TestUpdateTodoEndpoint:
    """Test PUT /todos/{id} endpoint"""
    
    def test_update_todo_success(self, auth_client, sample_todo):
        """Test updating a todo"""
        response = auth_client.put(
            f"/todos/{sample_todo.id}",
            json={"title": "Updated Title", "done": True}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["done"] is True
    
    def test_update_todo_not_found(self, auth_client):
        """Test updating non-existent todo"""
        response = auth_client.put(
            "/todos/99999",
            json={"title": "New Title"}
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_todo_validation_error(self, auth_client, sample_todo):
        """Test updating with invalid data"""
        response = auth_client.put(
            f"/todos/{sample_todo.id}",
            json={"title": ""}  # Empty title
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

class TestDeleteTodoEndpoint:
    """Test DELETE /todos/{id} endpoint"""
    
    def test_delete_todo_success(self, auth_client, sample_todo):
        """Test deleting a todo"""
        response = auth_client.delete(f"/todos/{sample_todo.id}")
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify it's deleted
        get_response = auth_client.get(f"/todos/{sample_todo.id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_todo_not_found(self, auth_client):
        """Test deleting non-existent todo"""
        response = auth_client.delete("/todos/99999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
```

**Run API tests:**
```bash
pytest tests/test_api.py -v
```

---

## **Testing Commands Reference**

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_crud.py -v

# Run specific test class
pytest tests/test_crud.py::TestCreateTodo -v

# Run specific test function
pytest tests/test_crud.py::TestCreateTodo::test_create_todo_with_ddl -v

# Run tests with coverage
pytest --cov=. --cov-report=html

# Run tests and stop on first failure
pytest -x

# Run tests in parallel (install pytest-xdist first)
pytest -n auto
```

---

## **Coverage Reporting**

### **Generate HTML Coverage Report**

```bash
pytest --cov=. --cov-report=html --cov-report=term
```

This creates a `htmlcov/` directory. Open `htmlcov/index.html` in your browser to see:
- Overall coverage percentage
- Line-by-line coverage for each file
- Uncovered lines highlighted

### **Aim for >80% Coverage**

Focus on covering:
- ✅ All CRUD functions
- ✅ All service layer functions
- ✅ All API endpoints
- ✅ Error handling paths
- ✅ Authentication flows
- ✅ User isolation (users can't access others' data)

---

## **Best Practices**

1. **Test Isolation**: Each test should be independent
2. **Descriptive Names**: Test names should describe what they test
3. **AAA Pattern**: Arrange, Act, Assert
4. **Test Edge Cases**: Empty lists, None values, invalid inputs
5. **Test Error Paths**: Not just success cases
6. **Use Fixtures**: Avoid code duplication
7. **Fast Tests**: Use in-memory database for speed

---

## **Common Pytest Patterns**

### **Testing Exceptions**
```python
with pytest.raises(TodoNotFoundException) as exc_info:
    get_todo_service(db, 99999, user_id)

assert exc_info.value.todo_id == 99999
```

### **Parametrized Tests**
```python
@pytest.mark.parametrize("title,expected", [
    ("Valid Title", True),
    ("", False),
    (None, False),
])
def test_title_validation(title, expected):
    # Test logic here
    pass
```

### **Async Tests**
```python
@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result is not None
```

---

## **Troubleshooting**

### **Issue: Tests fail with "database is locked"**
**Solution**: Use `check_same_thread=False` in SQLite connection

### **Issue: Tests interfere with each other**
**Solution**: Use `scope="function"` for fixtures to ensure isolation

### **Issue: Authentication tests fail**
**Solution**: Make sure to use `auth_client` fixture, not plain `client`

### **Issue: Coverage is low**
**Solution**: Add tests for error paths, edge cases, and all branches

---

## **Next Steps**

After completing this testing suite:
1. ✅ Run full test suite: `pytest -v`
2. ✅ Check coverage: `pytest --cov=. --cov-report=html`
3. ✅ Review uncovered lines in HTML report
4. ✅ Add tests for any missing coverage
5. ✅ Set up CI/CD to run tests automatically
6. ✅ Add pre-commit hooks to run tests before commits

**Congratulations!** You now have a comprehensive testing suite that ensures your FastAPI application works correctly and will catch bugs before they reach production.
