from unittest.mock import MagicMock, patch
from urllib.error import URLError

import pytest

from app.worker.tasks import send_webhook_event


def test_webhook_crud(client):
    res = client.post("/webhooks", json={"url": "http://example.com/webhook"})
    assert res.status_code == 200
    wh_id = res.json()["id"]

    res = client.get("/webhooks")
    assert res.status_code == 200
    assert len(res.json()) >= 1

    res = client.delete(f"/webhooks/{wh_id}")
    assert res.status_code == 200

    res = client.delete(f"/webhooks/{wh_id}")
    assert res.status_code == 404


@patch("urllib.request.urlopen")
def test_send_webhook_task_success(mock_urlopen):
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.__enter__.return_value = mock_response
    mock_urlopen.return_value = mock_response

    result = send_webhook_event("http://example.com", {"test": "data"})
    assert result == 200


@patch("urllib.request.urlopen")
@patch("app.worker.tasks.send_webhook_event.retry")
def test_send_webhook_task_retry_on_failure(mock_retry, mock_urlopen):
    mock_urlopen.side_effect = URLError("Server down")
    mock_retry.side_effect = Exception("Retry Triggered")

    with pytest.raises(Exception, match="Retry Triggered"):
        send_webhook_event("http://example.com", {"test": "data"})

    mock_urlopen.assert_called_once()
    mock_retry.assert_called_once()


def test_sale_creation_triggers_webhook(client):
    client.post("/webhooks", json={"url": "http://trigger.com/webhook"})

    with patch("app.worker.tasks.send_webhook_event.delay") as mock_delay:
        sale_data = {
            "user_id": 1,
            "items": [{"product_id": 1, "quantity": 1}],
        }
        res = client.post("/sales", json=sale_data)
        assert res.status_code == 200

        assert mock_delay.called
        args, _ = mock_delay.call_args
        assert "trigger.com" in args[0]
        assert args[1]["event"] == "sale.created"
