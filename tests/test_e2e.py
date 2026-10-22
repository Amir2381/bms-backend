import io
from unittest.mock import MagicMock, patch

from app.core.config import settings


@patch("app.routers.auth.sync_redis")
def test_full_system_scenario(mock_redis, client, monkeypatch):
    monkeypatch.setattr(settings, "ai_api_key", "mock-key")

    with patch("app.services.ai_assistant.OpenAI") as mock_openai_cls:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value.choices[0].message.content = (
            "AI Insights"
        )
        mock_openai_cls.return_value = mock_client

        # 1. Register a new user
        user_res = client.post(
            "/users",
            json={
                "full_name": "E2E User",
                "email": "e2e@example.com",
                "password": "strongpassword",
            },
        )
        assert user_res.status_code == 200

        # 2. Login
        login_res = client.post(
            "/auth/login",
            data={"username": "e2e@example.com", "password": "strongpassword"},
        )
        assert login_res.status_code == 200
        assert "access_token" in login_res.json()

        # 3. Create Category & Product with low stock
        cat_res = client.post("/categories", json={"name": "E2E Category"})
        assert cat_res.status_code == 200
        cat_id = cat_res.json()["id"]

        prod_res = client.post(
            "/products",
            json={
                "name": "E2E Product",
                "price": 100.0,
                "stock": 2,  # Low stock to trigger alert later
                "category_id": cat_id,
            },
        )
        assert prod_res.status_code == 200
        prod_id = prod_res.json()["id"]

        # 4. Import a Dirty CSV file
        csv_content = (
            "date,product,quantity,unit_price,seller\n"
            "2026-10-22,E2E Product,5,100.00,  \n"
            "invalid-date,E2E Product,1,-10, \n"
        )
        import_res = client.post(
            "/import/sales",
            files={
                "file": (
                    "e2e_sales.csv",
                    io.BytesIO(csv_content.encode("utf-8")),
                    "text/csv",
                )
            },
        )
        assert import_res.status_code == 200
        import_data = import_res.json()
        assert import_data["imported_rows"] == 1
        assert import_data["cleaning_report"]["invalid_rows"] == 1

        # 5. Create a standard sale to reduce stock to 0 and trigger alerts
        sale_res = client.post(
            "/sales",
            json={"user_id": 1, "items": [{"product_id": prod_id, "quantity": 2}]},
        )
        assert sale_res.status_code == 200

        # 6. Check Analytics & AI Insights
        metrics_res = client.get("/analytics/metrics")
        assert metrics_res.status_code == 200

        ai_res = client.get("/analytics/ai-insights")
        assert ai_res.status_code == 200
        assert ai_res.json()["markdown_content"] == "AI Insights"

        # 7. Test background report generation
        report_res = client.get("/analytics/dashboard/export")
        assert report_res.status_code == 200
        assert "job_id" in report_res.json()

        # 8. Verify System Alerts (CRITICAL alert for out of stock)
        alerts_res = client.get("/alerts")
        assert alerts_res.status_code == 200
        alerts_data = alerts_res.json()
        assert any(
            a["type"] == "CRITICAL" and "E2E Product" in a["message"]
            for a in alerts_data
        )

        # 9. Verify Audit Logs for the import action
        audit_res = client.get("/audit-logs")
        assert audit_res.status_code == 200
        audit_data = audit_res.json()
        assert any(log["action"] == "IMPORT_SALES" for log in audit_data)
