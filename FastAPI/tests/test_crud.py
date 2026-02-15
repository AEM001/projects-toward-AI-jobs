import pytest
from datetime import datetime, timedelta
from crud import(
    create_todo,list_todos,get_todo,update_todo,delete_todo,
    format_datetime)

from schemas import TodoCreate, TodoUpdate
from db import TodoDB
from pydantic import ValidationError

class TestFormatDatetime:
    def test_format_datetime_with_none(self):
        result=format_datetime(None)
        assert result is None
    
    def test_format_datetime_with_value(self):
        dt=datetime(2026,2,15,14,30,45)
        result=format_datetime(dt)
        assert result =="2026-02-15 14:30"

class TestCreateTodo:
    def test_create_todo(self,test_db,test_user):
        todo_data=TodoCreate(title="kill myself",ddl="2028-09-15 09:01")
        result=create_todo(test_db,todo_data,test_user.id)
        assert result.id is not None
        assert result.title=="kill myself"
        assert result.ddl==datetime(2028,9,15,9,1)
        assert result.done==False
        assert result.owner_id==test_user.id

    def test_create_todo_with_empty_title(self,test_db,test_user):
        with pytest.raises(ValidationError):
            TodoCreate(title="",ddl="2028-09-15 09:01")
    
    def test_create_todo_with_invalid_ddl(self,test_db,test_user):
        todo_data=TodoCreate(title="kill myself",ddl="never")
        result=create_todo(test_db,todo_data,test_user.id)
        # Should use default datetime, not None
        assert result.ddl is not None

class TestListTodos:
    def test_list_todos_empty(self,test_db,test_user):
        todos,total=list_todos(test_db,test_user.id,filter_today=False,filter_week=False)
        assert total==0
    
    def test_list_todos_with_create(self,test_db,test_user):
        create_todo(test_db,TodoCreate(title="finish task",ddl="2026-02-15 19:00"),test_user.id)
        todos,total=list_todos(test_db,test_user.id,filter_today=False,filter_week=False)
        assert total==1
    
    def test_list_todos_with_filter_today(self,test_db,test_user):
        create_todo(test_db,TodoCreate(title="finish task",ddl="2026-02-15 19:00"),test_user.id)
        create_todo(test_db,TodoCreate(title="plan task",ddl="2026-02-16 19:00"),test_user.id)
        todos,total=list_todos(test_db,test_user.id,filter_today=True,filter_week=False)
        assert total==1
        assert todos[0].title=="finish task"

    def test_list_todos_pagination(self,test_db,test_user):
        from datetime import datetime
        for i in range(10):
            todo=TodoDB(title=f"task {i}",ddl=datetime(2026,2,15,19,0),done=False,owner_id=test_user.id)
            test_db.add(todo)
        test_db.commit()  # Missing commit!
        
        todos,total=list_todos(test_db,test_user.id,filter_today=False,filter_week=False,skip=0,limit=5)
        assert total==10
        assert len(todos)==5

        todos,total=list_todos(test_db,test_user.id,filter_today=False,filter_week=False,skip=5,limit=5)
        assert total==10
        assert len(todos)==5

    def test_list_todos_title_filter(self, test_db, test_user):
        """Test filtering by title"""
        todo1 = TodoDB(title="Buy groceries", owner_id=test_user.id)
        todo2 = TodoDB(title="Read book", owner_id=test_user.id)
        test_db.add_all([todo1, todo2])
        test_db.commit()
        
        todos, total = list_todos(test_db, test_user.id, title="groceries", filter_today=False, filter_week=False)
        
        assert len(todos) == 1
        assert todos[0].title == "Buy groceries"
    
    def test_list_todos_sorting(self, test_db, test_user):
        """Test sorting by different fields"""
        todo1 = TodoDB(title="B Task", owner_id=test_user.id)
        todo2 = TodoDB(title="A Task", owner_id=test_user.id)
        test_db.add_all([todo1, todo2])
        test_db.commit()
        
        # Sort by title ascending
        todos, _ = list_todos(test_db, test_user.id, sort_by="title", sort_order="asc", filter_today=False, filter_week=False)
        assert todos[0].title == "A Task"
        assert todos[1].title == "B Task"
        
        # Sort by title descending
        todos, _ = list_todos(test_db, test_user.id, sort_by="title", sort_order="desc", filter_today=False, filter_week=False)
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
        user1_todos, _ = list_todos(test_db, test_user.id, filter_today=False, filter_week=False)
        assert len(user1_todos) == 1
        assert user1_todos[0].title == "User 1 Todo"
        
        user2_todos, _ = list_todos(test_db, other_user.id, filter_today=False, filter_week=False)
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
