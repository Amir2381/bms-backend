import json
import socket
import urllib.request
import os
from pathlib import Path
from datetime import datetime, timezone, timedelta
from urllib.error import URLError, HTTPError

from sqlalchemy import select

from app.db.database import SessionLocal
from app.models.system_alert import SystemAlert
from app.models.user import User
from app.repositories import sale_repository
from app.worker.celery_app import celery_app
from app.services.analytics.service import AnalyticsService
from app.services.reporting.csv_strategy import CsvReportStrategy
from app.services.reporting.excel_strategy import (
    ExcelReportStrategy,
    MultiSheetExcelReportStrategy,
)
from app.services.reporting.generator import ReportGenerator


@celery_app.task
def check_and_create_alerts(branch_id: int):
    with SessionLocal() as db:
        alerts_data = sale_repository.get_inventory_alerts(
            db, days_threshold=3, lookback_days=30, branch_id=branch_id
        )
        for alert in alerts_data:
            if alert["current_stock"] == 0:
                alert_type = "CRITICAL"
                msg = f"Product '{alert['product_name']}' is out of stock!"
            else:
                alert_type = "WARNING"
                msg = f"Product '{alert['product_name']}' will run out in ~{round(alert['days_remaining'])} days."

            new_alert = SystemAlert(
                branch_id=branch_id,
                type=alert_type,
                message=msg,
            )
            db.add(new_alert)
        db.commit()


@celery_app.task
def check_at_risk_customers():
    with SessionLocal() as db:
        rfm_data = sale_repository.get_rfm_data(db, limit=1000)

        cutoff_date = datetime.now(timezone.utc) - timedelta(days=7)

        for item in rfm_data:
            r = item["recency_days"]
            f = item["frequency"]

            if r > 90 and f < 2:
                customer_name = item["customer_name"]
                msg = f"Customer '{customer_name}' has reached the 'At Risk' segment."

                stmt = select(SystemAlert).where(
                    SystemAlert.message == msg, SystemAlert.created_at >= cutoff_date
                )
                existing_alert = db.scalars(stmt).first()

                if not existing_alert:
                    new_alert = SystemAlert(
                        branch_id=None,
                        type="WARNING",
                        message=msg,
                    )
                    db.add(new_alert)

        db.commit()


@celery_app.task(bind=True, max_retries=5)
def send_webhook_event(self, url: str, payload: dict):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.status
    except (URLError, HTTPError, socket.timeout) as exc:
        countdown = 2 ** (self.request.retries + 1)
        raise self.retry(exc=exc, countdown=countdown)


@celery_app.task(bind=True)
def generate_report_task(self, report_type: str, user_id: int, params: dict):
    job_id = self.request.id
    reports_dir = Path("storage/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)

    export_format = params.get("export_format", "excel").lower()
    extension = "xlsx" if export_format == "excel" else "csv"

    if report_type == "dashboard":
        extension = "xlsx"

    file_path = reports_dir / f"{job_id}.{extension}"

    with SessionLocal() as db:
        current_user = db.query(User).get(user_id)
        if not current_user:
            return {"status": "failed", "error": "User not found"}

        service = AnalyticsService(db)

        start_date_str = params.get("start_date")
        end_date_str = params.get("end_date")
        start_date = (
            datetime.strptime(start_date_str, "%Y-%m-%d").date()
            if start_date_str
            else None
        )
        end_date = (
            datetime.strptime(end_date_str, "%Y-%m-%d").date() if end_date_str else None
        )

        branch_id = params.get("branch_id")
        limit = params.get("limit", 100)
        period = params.get("period", "daily")

        if report_type == "dashboard":
            metrics_data = service.get_summary_metrics(
                current_user, start_date, end_date, branch_id
            )
            metrics_dict = {
                "Total Sales": str(metrics_data.total_sales),
                "Total Profit": str(metrics_data.total_profit),
                "Profit Margin (%)": str(metrics_data.profit_margin),
                "Total Transactions": metrics_data.total_transactions,
                "Average Order Value": str(metrics_data.average_order_value),
                "Highest Sale": (
                    str(metrics_data.highest_sale)
                    if metrics_data.highest_sale
                    else "N/A"
                ),
                "Lowest Sale": (
                    str(metrics_data.lowest_sale) if metrics_data.lowest_sale else "N/A"
                ),
                "Average Daily Sales": str(metrics_data.average_daily_sales),
                "Sold Products Count": metrics_data.sold_products_count,
                "Average CLV": str(metrics_data.average_clv),
            }
            metrics_sheet = {
                "headers": ["Metric", "Value"],
                "data": [{"Metric": k, "Value": v} for k, v in metrics_dict.items()],
            }

            trend_data = service.get_sales_trend(
                current_user, "daily", start_date, end_date, branch_id
            )
            trends_sheet = {
                "headers": ["Period", "Revenue", "Transaction Count"],
                "data": [
                    {
                        "Period": point.period.isoformat(),
                        "Revenue": str(point.revenue),
                        "Transaction Count": point.transaction_count,
                    }
                    for point in trend_data.points
                ],
            }

            product_data = service.get_product_performance(
                current_user,
                limit=10,
                start_date=start_date,
                end_date=end_date,
                branch_id=branch_id,
            )
            products_sheet = {
                "headers": [
                    "Product ID",
                    "Product Name",
                    "Quantity Sold",
                    "Revenue",
                    "Revenue Share (%)",
                ],
                "data": [
                    {
                        "Product ID": p.product_id,
                        "Product Name": p.product_name,
                        "Quantity Sold": p.quantity_sold,
                        "Revenue": str(p.revenue),
                        "Revenue Share (%)": str(p.revenue_share),
                    }
                    for p in product_data.products
                ],
            }

            sheets_data = {
                "Dashboard Metrics": metrics_sheet,
                "Sales Trends": trends_sheet,
                "Top Products": products_sheet,
            }

            strategy = MultiSheetExcelReportStrategy()
            with open(file_path, "wb") as f:
                for chunk in strategy.generate_multi_sheet(sheets_data):
                    f.write(chunk)

        else:
            strategy = (
                ExcelReportStrategy()
                if export_format == "excel"
                else CsvReportStrategy()
            )
            generator = ReportGenerator(strategy)
            headers = []
            data = []

            if report_type == "sales_trends":
                trend_data = service.get_sales_trend(
                    current_user, period, start_date, end_date, branch_id
                )
                headers = ["Period", "Revenue", "Transaction Count"]
                data = [
                    {
                        "Period": p.period.isoformat(),
                        "Revenue": str(p.revenue),
                        "Transaction Count": p.transaction_count,
                    }
                    for p in trend_data.points
                ]

            elif report_type == "product_performance":
                perf_data = service.get_product_performance(
                    current_user, limit, start_date, end_date, branch_id
                )
                headers = [
                    "Product ID",
                    "Product Name",
                    "Quantity Sold",
                    "Revenue",
                    "Revenue Share (%)",
                ]
                data = [
                    {
                        "Product ID": p.product_id,
                        "Product Name": p.product_name,
                        "Quantity Sold": p.quantity_sold,
                        "Revenue": str(p.revenue),
                        "Revenue Share (%)": str(p.revenue_share),
                    }
                    for p in perf_data.products
                ]

            elif report_type == "category_performance":
                cat_data = service.get_category_performance(
                    current_user, limit, start_date, end_date, branch_id
                )
                headers = [
                    "Category ID",
                    "Category Name",
                    "Quantity Sold",
                    "Revenue",
                    "Revenue Share (%)",
                ]
                data = [
                    {
                        "Category ID": c.category_id if c.category_id else "N/A",
                        "Category Name": c.category_name,
                        "Quantity Sold": c.quantity_sold,
                        "Revenue": str(c.revenue),
                        "Revenue Share (%)": str(c.revenue_share),
                    }
                    for c in cat_data.categories
                ]

            elif report_type == "top_customers":
                cust_data = service.get_top_customers(
                    current_user, limit, start_date, end_date, branch_id
                )
                headers = [
                    "Customer ID",
                    "Name",
                    "Phone",
                    "Revenue",
                    "Profit",
                    "Transaction Count",
                ]
                data = [
                    {
                        "Customer ID": c.customer_id,
                        "Name": c.customer_name,
                        "Phone": c.customer_phone,
                        "Revenue": str(c.revenue),
                        "Profit": str(c.profit),
                        "Transaction Count": c.transaction_count,
                    }
                    for c in cust_data.customers
                ]

            mode = "wb" if export_format == "excel" else "w"
            newline = "" if export_format == "csv" else None
            encoding = "utf-8" if export_format == "csv" else None

            with open(file_path, mode, newline=newline, encoding=encoding) as f:
                for chunk in generator.generate(headers, data):
                    if isinstance(chunk, bytes) and mode == "w":
                        f.write(chunk.decode("utf-8"))
                    elif isinstance(chunk, str) and mode == "wb":
                        f.write(chunk.encode("utf-8"))
                    else:
                        f.write(chunk)

    return {"status": "completed", "file_path": str(file_path)}
