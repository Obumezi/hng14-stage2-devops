from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import sys
import os

# Add backend directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from main import app

client = TestClient(app)


def test_health():
    """Test health check endpoint returns ok status"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@patch("main.r")
def test_create_job(mock_redis):
    """Test job creation pushes to Redis queue"""
    mock_redis.lpush.return_value = 1
    mock_redis.hset.return_value = True
    
    response = client.post("/jobs")
    assert response.status_code == 200
    assert "job_id" in response.json()
    
    # Verify Redis calls
    mock_redis.lpush.assert_called_once()
    mock_redis.hset.assert_called_once()


@patch("main.r")
def test_get_job_completed(mock_redis):
    """Test retrieving a completed job"""
    mock_redis.hget.return_value = "completed"
    
    response = client.get("/jobs/test-job-id")
    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == "test-job-id"
    assert data["status"] == "completed"


@patch("main.r")
def test_get_job_not_found(mock_redis):
    """Test retrieving non-existent job returns 404"""
    mock_redis.hget.return_value = None
    
    response = client.get("/jobs/nonexistent-job")
    assert response.status_code == 404
    assert response.json() == {"error": "not found"}