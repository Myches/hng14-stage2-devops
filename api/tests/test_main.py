import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

# Patch redis before importing app
with patch("redis.Redis") as mock_redis_class:
    mock_redis = MagicMock()
    mock_redis_class.return_value = mock_redis
    from main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_mocks():
    mock_redis.reset_mock()


def test_health_check_ok():
    mock_redis.ping.return_value = True
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_health_check_redis_down():
    mock_redis.ping.side_effect = Exception("Connection refused")
    response = client.get("/health")
    assert response.status_code == 503


def test_create_job_returns_job_id():
    mock_redis.lpush.return_value = 1
    mock_redis.hset.return_value = 1
    response = client.post("/jobs")
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert len(data["job_id"]) == 36  # UUID format


def test_create_job_pushes_to_queue():
    mock_redis.lpush.return_value = 1
    mock_redis.hset.return_value = 1
    response = client.post("/jobs")
    job_id = response.json()["job_id"]
    mock_redis.lpush.assert_called_once_with("jobs", job_id)


def test_get_job_queued_status():
    mock_redis.hget.return_value = "queued"
    response = client.get("/jobs/test-job-123")
    assert response.status_code == 200
    assert response.json()["status"] == "queued"


def test_get_job_completed_status():
    mock_redis.hget.return_value = "completed"
    response = client.get("/jobs/test-job-123")
    assert response.status_code == 200
    assert response.json()["status"] == "completed"


def test_get_job_not_found():
    mock_redis.hget.return_value = None
    response = client.get("/jobs/nonexistent-job")
    assert response.status_code == 404
    assert "error" in response.json()