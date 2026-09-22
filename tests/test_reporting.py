from fastapi.testclient import TestClient

from app.services.reporting.csv_strategy import CsvReportStrategy
from app.services.reporting.generator import ReportGenerator


def test_csv_strategy_generation():
    strategy = CsvReportStrategy()
    headers = ["id", "name"]
    data = [{"id": 1, "name": "Amir"}, {"id": 2, "name": "Reza"}]

    generator = ReportGenerator(strategy)
    result = list(generator.generate(headers, data))

    assert len(result) == 3
    assert "id,name" in result[0].strip()
    assert "1,Amir" in result[1].strip()
    assert "2,Reza" in result[2].strip()


def test_export_analytics_endpoints(client: TestClient):
    response = client.get("/analytics/products/performance/export?limit=10")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert (
        "attachment; filename=product_performance.csv"
        in response.headers["content-disposition"]
    )

    response_categories = client.get(
        "/analytics/categories/performance/export?limit=10"
    )
    assert response_categories.status_code == 200
    assert response_categories.headers["content-type"] == "text/csv; charset=utf-8"
    assert (
        "attachment; filename=category_performance.csv"
        in response_categories.headers["content-disposition"]
    )

    response_trends = client.get("/analytics/trends/export?period=daily")
    assert response_trends.status_code == 200
    assert response_trends.headers["content-type"] == "text/csv; charset=utf-8"
    assert (
        "attachment; filename=sales_trends.csv"
        in response_trends.headers["content-disposition"]
    )
