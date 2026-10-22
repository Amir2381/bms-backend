from app.models.system_alert import SystemAlert
from tests.database import TestingSessionLocal


def test_get_alerts_and_mark_read(client):
    db = TestingSessionLocal()
    try:
        alert = SystemAlert(type="WARNING", message="Test Alert", is_read=False)
        db.add(alert)
        db.commit()
        db.refresh(alert)
        alert_id = alert.id
    finally:
        db.close()

    res = client.get("/alerts")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1
    assert any(a["id"] == alert_id for a in data)

    res_put = client.put(f"/alerts/{alert_id}/read")
    assert res_put.status_code == 200
    assert res_put.json()["is_read"] is True

    res_unread = client.get("/alerts?unread_only=true")
    assert res_unread.status_code == 200
    unread_data = res_unread.json()
    assert not any(a["id"] == alert_id for a in unread_data)


def test_mark_alert_read_not_found(client):
    res = client.put("/alerts/99999/read")
    assert res.status_code == 404
