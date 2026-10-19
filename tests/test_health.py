from unittest.mock import patch
from fastapi.testclient import TestClient

from app.core.redis import sync_redis
from app.worker.celery_app import celery_app


def test_health_check_all_healthy(client: TestClient):
    with patch.object(sync_redis, "ping", return_value=True), patch.object(
        celery_app.control, "ping", return_value=[{"worker1": {"ok": "pong"}}]
    ):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["services"]["database"] == "healthy"
        assert data["services"]["redis"] == "healthy"
        assert data["services"]["celery"] == "healthy"


def test_health_check_unhealthy_services(client: TestClient):
    with patch.object(
        sync_redis, "ping", side_effect=Exception("Redis connection error")
    ), patch.object(celery_app.control, "ping", return_value=[]):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["services"]["database"] == "healthy"
        assert data["services"]["redis"] == "unhealthy"
        assert "unhealthy" in data["services"]["celery"]
