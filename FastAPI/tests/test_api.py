"""
API Integration Tests for FastAPI Todo Application

Tests all REST API endpoints including authentication and todo CRUD operations.
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta


class TestAuthAPI:
    """Test authentication endpoints"""

    def test_register_success(self, client):
        """Test user registration"""
        response = client.post(
            "/auth/register",
            json={"email": "newuser@gmail.com", "password": "securepass123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "newuser@gmail.com"
        assert "id" in data

    def test_register_duplicate_email(self, client, test_user):
        """Test registration with existing email fails"""
        response = client.post(
            "/auth/register",
            json={"email": "test@gmail.com", "password": "password123"}
        )
        assert response.status_code == 400
        assert "Email has been registered" in response.json()["detail"]

    def test_login_success(self, client, test_user):
        """Test successful login"""
        response = client.post(
            "/auth/login",
            json={"email": "test@gmail.com", "password": "test_password"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, test_user):
        """Test login with wrong password"""
        response = client.post(
            "/auth/login",
            json={"email": "test@gmail.com", "password": "wrongpassword"}
        )
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user"""
        response = client.post(
            "/auth/login",
            json={"email": "nonexistent@gmail.com", "password": "password123"}
        )
        assert response.status_code == 401

    def test_get_current_user_success(self, auth_client):
        """Test getting current user info with valid token"""
        response = auth_client.get("/auth/me")
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@gmail.com"
        assert "id" in data

    def test_get_current_user_no_token(self, client):
        """Test accessing protected endpoint without token"""
        response = client.get("/auth/me")
        assert response.status_code == 403

    def test_get_current_user_invalid_token(self, client):
        """Test with invalid token"""
        client.headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/auth/me")
        assert response.status_code == 401


class TestTodoAPI:
    """Test Todo CRUD endpoints"""

    def test_create_todo_success(self, auth_client):
        """Test creating a new todo"""
        ddl = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M")
        response = auth_client.post(
            "/todos",
            json={"title": "Test API Todo", "ddl": ddl}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test API Todo"
        assert data["ddl"] == ddl
        assert data["done"] == False
        assert "id" in data
        assert "owner_id" in data

    def test_create_todo_without_ddl(self, auth_client):
        """Test creating a todo without deadline - gets default value"""
        response = auth_client.post(
            "/todos",
            json={"title": "No Deadline Todo"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "No Deadline Todo"
        # API sets default ddl to tomorrow 21:00 when not provided
        assert data["ddl"] is not None  # Should have default value

    def test_create_todo_unauthorized(self, client):
        """Test creating todo without authentication"""
        response = client.post(
            "/todos",
            json={"title": "Unauthorized Todo"}
        )
        assert response.status_code == 403

    def test_list_todos_empty(self, auth_client):
        """Test listing todos when empty"""
        response = auth_client.get("/todos")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0
        assert data["page"] == 0
        assert data["pages"] == 1

    def test_list_todos_with_data(self, auth_client, sample_todo):
        """Test listing todos with existing data"""
        response = auth_client.get("/todos")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["total"] == 1
        assert data["items"][0]["title"] == sample_todo.title

    def test_list_todos_pagination(self, auth_client, test_db, test_user):
        """Test pagination in list todos"""
        # Create multiple todos
        from db import TodoDB
        for i in range(15):
            todo = TodoDB(title=f"Todo {i}", owner_id=test_user.id)
            test_db.add(todo)
        test_db.commit()

        # Test first page
        response = auth_client.get("/todos?skip=0&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 10
        assert data["total"] == 15
        assert data["pages"] == 2

        # Test second page
        response = auth_client.get("/todos?skip=10&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 5

    def test_list_todos_search_by_title(self, auth_client, sample_todo):
        """Test searching todos by title"""
        response = auth_client.get(f"/todos?title={sample_todo.title}")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["title"] == sample_todo.title

    def test_list_todos_unauthorized(self, client):
        """Test listing todos without authentication"""
        response = client.get("/todos")
        assert response.status_code == 403

    def test_get_todo_success(self, auth_client, sample_todo):
        """Test getting a specific todo"""
        response = auth_client.get(f"/todos/{sample_todo.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_todo.id
        assert data["title"] == sample_todo.title

    def test_get_todo_not_found(self, auth_client):
        """Test getting non-existent todo"""
        response = auth_client.get("/todos/99999")
        assert response.status_code == 404
        assert "Todo with id 99999 not found" in response.json()["detail"]

    def test_get_todo_unauthorized(self, client, sample_todo):
        """Test getting todo without authentication"""
        response = client.get(f"/todos/{sample_todo.id}")
        assert response.status_code == 403

    def test_get_todo_wrong_owner(self, auth_client, test_db):
        """Test getting todo owned by another user"""
        from db import TodoDB, UserDB
        from main import get_password_hash

        # Create another user and their todo
        other_user = UserDB(email="other@gmail.com", hashed_password=get_password_hash("pass"))
        test_db.add(other_user)
        test_db.commit()
        test_db.refresh(other_user)

        other_todo = TodoDB(title="Other's todo", owner_id=other_user.id)
        test_db.add(other_todo)
        test_db.commit()
        test_db.refresh(other_todo)

        # Try to access with current user
        response = auth_client.get(f"/todos/{other_todo.id}")
        assert response.status_code == 404

    def test_update_todo_success(self, auth_client, sample_todo):
        """Test updating a todo"""
        response = auth_client.put(
            f"/todos/{sample_todo.id}",
            json={"title": "Updated Title", "done": True}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["done"] == True
        assert data["id"] == sample_todo.id

    def test_update_todo_partial(self, auth_client, sample_todo):
        """Test partial update (only title)"""
        response = auth_client.put(
            f"/todos/{sample_todo.id}",
            json={"title": "Only Title Updated"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Only Title Updated"
        assert data["done"] == sample_todo.done  # Unchanged

    def test_update_todo_not_found(self, auth_client):
        """Test updating non-existent todo"""
        response = auth_client.put(
            "/todos/99999",
            json={"title": "New Title"}
        )
        assert response.status_code == 404

    def test_update_todo_unauthorized(self, client, sample_todo):
        """Test updating without authentication"""
        response = client.put(
            f"/todos/{sample_todo.id}",
            json={"title": "Hacked Title"}
        )
        assert response.status_code == 403

    def test_delete_todo_success(self, auth_client, sample_todo):
        """Test deleting a todo"""
        response = auth_client.delete(f"/todos/{sample_todo.id}")
        assert response.status_code == 204

        # Verify it's deleted
        response = auth_client.get(f"/todos/{sample_todo.id}")
        assert response.status_code == 404

    def test_delete_todo_not_found(self, auth_client):
        """Test deleting non-existent todo"""
        response = auth_client.delete("/todos/99999")
        assert response.status_code == 404

    def test_delete_todo_unauthorized(self, client, sample_todo):
        """Test deleting without authentication"""
        response = client.delete(f"/todos/{sample_todo.id}")
        assert response.status_code == 403


class TestValidationAPI:
    """Test input validation"""

    def test_create_todo_empty_title(self, auth_client):
        """Test creating todo with empty title fails validation"""
        response = auth_client.post(
            "/todos",
            json={"title": ""}
        )
        assert response.status_code == 422

    def test_create_todo_missing_title(self, auth_client):
        """Test creating todo without title field"""
        response = auth_client.post(
            "/todos",
            json={}
        )
        assert response.status_code == 422

    def test_create_todo_invalid_ddl_format(self, auth_client):
        """Test creating todo with invalid ddl format"""
        response = auth_client.post(
            "/todos",
            json={"title": "Test", "ddl": "invalid-date"}
        )
        # The service should handle this gracefully (ddl becomes None)
        assert response.status_code in [201, 422]


class TestDebugAPI:
    """Test debug endpoints"""

    def test_tx_fail(self, auth_client):
        """Test transaction failure endpoint"""
        response = auth_client.post("/debug/tx-fail")
        assert response.status_code == 400

    def test_tx_atomic(self, auth_client):
        """Test transaction atomicity endpoint"""
        response = auth_client.post("/debug/tx-atomic")
        assert response.status_code == 400
