"""
Tests for API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "services" in data


def test_create_research_job():
    """Test creating a research job."""
    payload = {
        "query": "What is quantum computing?",
        "user_id": "test_user",
        "max_results": 5,
        "include_citations": True
    }
    
    response = client.post("/api/v1/research", json=payload)
    assert response.status_code == 202
    data = response.json()
    assert "job_id" in data
    assert data["query"] == payload["query"]
    assert data["status"] in ["pending", "processing"]


def test_get_research_job():
    """Test getting research job status."""
    # First create a job
    payload = {
        "query": "Test query",
        "max_results": 3
    }
    create_response = client.post("/api/v1/research", json=payload)
    job_id = create_response.json()["job_id"]
    
    # Get job status
    response = client.get(f"/api/v1/research/{job_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == job_id


def test_get_nonexistent_job():
    """Test getting a nonexistent job."""
    response = client.get("/api/v1/research/nonexistent-id")
    assert response.status_code == 404


def test_list_jobs():
    """Test listing all jobs."""
    response = client.get("/api/v1/jobs?limit=10&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "jobs" in data


def test_invalid_research_request():
    """Test creating research job with invalid data."""
    payload = {
        "query": "a",  # Too short
        "max_results": 100  # Too many
    }
    
    response = client.post("/api/v1/research", json=payload)
    assert response.status_code == 422  # Validation error