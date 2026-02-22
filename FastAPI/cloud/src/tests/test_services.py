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