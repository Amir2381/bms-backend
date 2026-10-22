from app.models.audit_log import AuditLog
from tests.database import TestingSessionLocal


def test_get_audit_logs(client):
    db = TestingSessionLocal()
    try:
        log = AuditLog(
            action="TEST_ACTION", entity_type="Test", details={"key": "value"}
        )
        db.add(log)
        db.commit()
    finally:
        db.close()

    res = client.get("/audit-logs")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1
    assert any(a["action"] == "TEST_ACTION" for a in data)
