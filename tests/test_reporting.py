import io

from fastapi.testclient import TestClient
from openpyxl import load_workbook

from app.services.reporting.csv_strategy import CsvReportStrategy
from app.services.reporting.excel_strategy import (
    ExcelReportStrategy,
    MultiSheetExcelReportStrategy,
)
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


def test_multi_sheet_excel_strategy_generation():
    strategy = MultiSheetExcelReportStrategy()
    sheets_data = {
        "Sheet1": {"headers": ["id", "name"], "data": [{"id": 1, "name": "Amir"}]},
        "Sheet2": {"headers": ["value"], "data": [{"value": 100}]},
    }

    result_bytes = b"".join(list(strategy.generate_multi_sheet(sheets_data)))
    workbook = load_workbook(filename=io.BytesIO(result_bytes))

    assert "Sheet1" in workbook.sheetnames
    assert "Sheet2" in workbook.sheetnames

    ws1 = workbook["Sheet1"]
    rows1 = list(ws1.iter_rows(values_only=True))
    assert rows1[0] == ("id", "name")
    assert rows1[1] == (1, "Amir")

    ws2 = workbook["Sheet2"]
    rows2 = list(ws2.iter_rows(values_only=True))
    assert rows2[0] == ("value",)
    assert rows2[1] == (100,)


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


def test_export_dashboard_excel(client: TestClient):
    response = client.get("/analytics/dashboard/export")
    assert response.status_code == 200
    assert (
        response.headers["content-type"]
        == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    assert (
        "attachment; filename=dashboard_report.xlsx"
        in response.headers["content-disposition"]
    )
