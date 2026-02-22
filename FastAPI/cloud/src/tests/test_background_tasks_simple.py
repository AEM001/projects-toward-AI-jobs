"""
Simple tests for background task integration in API endpoints
"""
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from main import app

class TestBackgroundTasks:
    """Test background task integration"""
    
    def test_create_todo_triggers_background_email(self, auth_client):
        """Test that creating a todo triggers background email task"""
        with patch('main.send_todo_created_email') as mock_email:
            response = auth_client.post(
                "/todos",
                json={"title": "Background Test Todo", "ddl": "2026-02-20 18:00"}
            )
            
            assert response.status_code == 201
            data = response.json()
            assert data["title"] == "Background Test Todo"
            
            # Verify background task was added (email function called)
            mock_email.assert_called_once()
    
    def test_create_todo_without_ddl_triggers_background_email(self, auth_client):
        """Test background email works when todo has no deadline"""
        with patch('main.send_todo_created_email') as mock_email:
            response = auth_client.post(
                "/todos",
                json={"title": "No Deadline Todo"}
            )
            
            assert response.status_code == 201
            
            # Verify background task was called
            mock_email.assert_called_once()
    
    def test_background_task_does_not_block_response(self, auth_client):
        """Test that background tasks don't block the API response"""
        with patch('main.send_todo_created_email') as mock_email:
            # Make email function slow to simulate network delay
            mock_email.side_effect = lambda *args: __import__('time').sleep(0.5)
            
            import time
            start_time = time.time()
            
            response = auth_client.post(
                "/todos",
                json={"title": "Fast Response Todo"}
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # Response should be fast even though email function is slow
            assert response.status_code == 201
            assert response_time < 0.3  # Should be much less than 0.5s email delay
            
            # Email should still be called
            mock_email.assert_called_once()
    
    def test_background_task_failure_does_not_affect_todo_creation(self, auth_client):
        """Test that background task failures don't affect the main operation"""
        with patch('main.send_todo_created_email') as mock_email:
            # Make email function raise an exception
            mock_email.side_effect = Exception("Email service down")
            
            response = auth_client.post(
                "/todos",
                json={"title": "Todo Despite Email Failure"}
            )
            
            # Todo should still be created successfully
            assert response.status_code == 201
            data = response.json()
            assert data["title"] == "Todo Despite Email Failure"
            
            # Background task was still attempted
            mock_email.assert_called_once()
