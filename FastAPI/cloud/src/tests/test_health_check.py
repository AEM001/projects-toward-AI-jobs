"""
Tests for health check endpoint
"""
import pytest
from datetime import datetime


class TestHealthCheck:
    """Test health check endpoint functionality"""

    def test_health_check_returns_200(self, client):
        """Test that health check returns 200 OK"""
        response = client.get("/health")
        
        assert response.status_code == 200

    def test_health_check_returns_healthy_status(self, client):
        """Test that health check returns healthy status"""
        response = client.get("/health")
        
        data = response.json()
        assert data["status"] == "healthy"

    def test_health_check_returns_timestamp(self, client):
        """Test that health check includes timestamp"""
        response = client.get("/health")
        
        data = response.json()
        assert "timestamp" in data
        
        # Verify timestamp is a valid ISO format
        try:
            datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
        except ValueError:
            pytest.fail(f"Invalid timestamp format: {data['timestamp']}")

    def test_health_check_no_authentication_required(self, client):
        """Test that health check works without authentication"""
        # Don't set any auth headers
        response = client.get("/health")
        
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
