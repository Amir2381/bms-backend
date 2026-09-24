import io

from fastapi.testclient import TestClient
from openpyxl import load_workbook

from app.services.reporting.csv_strategy import CsvReportStrategy
from app.services.reporting.excel_strategy import ExcelReportStrategy
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


def test_excel_strategy_generation():
    strategy = ExcelReportStrategy()
    headers = ["id", "name"]
    data = [{"id": 1, "name": "Amir"}, {"id": 2, "name": "Reza"}]

    generator = ReportGenerator(strategy)
    result_bytes = b"".join(list(generator.generate(headers, data)))

    workbook = load_workbook(filename=io.BytesIO(result_bytes))
    worksheet = workbook.active

    rows = list(worksheet.iter_rows(values_only=True))
    assert rows[0] == ("id", "name")
    assert rows[1] == (1, "Amir")
    assert rows[2] == (2, "Reza")


def test_export_analytics_endpoints_csv(client: TestClient):
    response = client.get(
        "/analytics/products/performance/export?limit=10&export_format=csv"
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert (
        "attachment; filename=product_performance.csv"
        in response.headers["content-disposition"]
    )

    response_categories = client.get(
        "/analytics/categories/performance/export?limit=10&export_format=csv"
    )
    assert response_categories.status_code == 200
    assert response_categories.headers["content-type"] == "text/csv; charset=utf-8"
    assert (
        "attachment; filename=category_performance.csv"
        in response_categories.headers["content-disposition"]
    )

    response_trends = client.get(
        "/analytics/trends/export?period=daily&export_format=csv"
    )
    assert response_trends.status_code == 200
    assert response_trends.headers["content-type"] == "text/csv; charset=utf-8"
    assert (
        "attachment; filename=sales_trends.csv"
        in response_trends.headers["content-disposition"]
    )


def test_export_analytics_endpoints_excel(client: TestClient):
    response_trends = client.get(
        "/analytics/trends/export?period=daily&export_format=excel"
    )
    assert response_trends.status_code == 200
    assert (
        response_trends.headers["content-type"]
        == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    assert (
        "attachment; filename=sales_trends.xlsx"
        in response_trends.headers["content-disposition"]
    )
