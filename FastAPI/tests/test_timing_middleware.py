"""
Tests for request timing middleware
"""
import pytest


class TestRequestTimingMiddleware:
    """Test request timing middleware functionality"""

    def test_request_timing_header_present(self, auth_client):
        """Test that timing header is added to responses"""
        response = auth_client.get("/todos")

        assert response.status_code == 200
        # Check that X-Request-Duration header is present
        assert "X-Request-Duration" in response.headers
        # Verify it's in the expected format (e.g., "0.0234s")
        duration_str = response.headers["X-Request-Duration"]
        assert duration_str.endswith("s")
        # Should be parseable as a float
        duration = float(duration_str.replace("s", ""))
        assert duration >= 0  # Duration should be non-negative

    def test_request_timing_header_on_all_endpoints(self, auth_client):
        """Test that timing header appears on different endpoints"""
        # Test GET
        response = auth_client.get("/todos")
        assert "X-Request-Duration" in response.headers

        # Test POST
        response = auth_client.post(
            "/todos",
            json={"title": "Timing Test Todo"}
        )
        assert response.status_code == 201
        assert "X-Request-Duration" in response.headers

    def test_request_duration_is_reasonable(self, auth_client):
        """Test that reported duration is reasonable (not negative, not huge)"""
        response = auth_client.get("/todos")

        duration_str = response.headers["X-Request-Duration"]
        duration = float(duration_str.replace("s", ""))

        # Should be non-negative
        assert duration >= 0

        # Should be reasonable (less than 10 seconds for a simple request)
        assert duration < 10.0, f"Request took {duration}s, which seems too long"
