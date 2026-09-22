from datetime import date
from typing import Any, Iterator

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.analytics import (
    CategoryPerformanceItem,
    CategoryPerformanceResponse,
    ProductPerformanceItem,
    ProductPerformanceResponse,
    SalesTrendItem,
    SalesTrendResponse,
    SummaryMetricsResponse,
)
from app.services.analytics.service import AnalyticsService
from app.services.reporting.utils import stream_csv_response

router = APIRouter(prefix="/analytics", tags=["analytics"])


def get_analytics_service(db: Session = Depends(get_db)) -> AnalyticsService:
    return AnalyticsService(db)


@router.get("/metrics", response_model=SummaryMetricsResponse)
def get_summary_metrics(
    start_date: date | None = Query(None, description="Start date for filtering"),
    end_date: date | None = Query(None, description="End date for filtering"),
    current_user: User = Depends(get_current_user),
    service: AnalyticsService = Depends(get_analytics_service),
):
    return service.get_summary_metrics(start_date, end_date)


@router.get("/trends", response_model=SalesTrendResponse)
def get_sales_trends(
    period: str = Query("daily", description="Time period for the trend"),
    start_date: date | None = Query(None, description="Start date for filtering"),
    end_date: date | None = Query(None, description="End date for filtering"),
    current_user: User = Depends(get_current_user),
    service: AnalyticsService = Depends(get_analytics_service),
):
    trend_data = service.get_sales_trend(period, start_date, end_date)

    return SalesTrendResponse(
        trends=[
            SalesTrendItem(
                date=point.period,
                revenue=point.revenue,
                transaction_count=point.transaction_count,
            )
            for point in trend_data.points
        ]
    )


@router.get("/trends/export")
def export_sales_trends(
    period: str = Query("daily", description="Time period for the trend"),
    start_date: date | None = Query(None, description="Start date for filtering"),
    end_date: date | None = Query(None, description="End date for filtering"),
    current_user: User = Depends(get_current_user),
    service: AnalyticsService = Depends(get_analytics_service),
):
    trend_data = service.get_sales_trend(period, start_date, end_date)

    def data_generator() -> Iterator[dict[str, Any]]:
        for point in trend_data.points:
            yield {
                "Period": point.period.isoformat(),
                "Revenue": str(point.revenue),
                "Transaction Count": point.transaction_count,
            }

    headers = ["Period", "Revenue", "Transaction Count"]
    return stream_csv_response(headers, data_generator(), "sales_trends.csv")


@router.get("/products/performance", response_model=ProductPerformanceResponse)
def get_product_performance(
    limit: int = Query(10, description="Top N products", ge=1, le=100),
    start_date: date | None = Query(None, description="Start date for filtering"),
    end_date: date | None = Query(None, description="End date for filtering"),
    current_user: User = Depends(get_current_user),
    service: AnalyticsService = Depends(get_analytics_service),
):
    performance_data = service.get_product_performance(limit, start_date, end_date)

    return ProductPerformanceResponse(
        products=[
            ProductPerformanceItem(
                product_id=p.product_id,
                product_name=p.product_name,
                quantity_sold=p.quantity_sold,
                revenue=p.revenue,
                revenue_share=p.revenue_share,
            )
            for p in performance_data.products
        ]
    )


@router.get("/products/performance/export")
def export_product_performance(
    limit: int = Query(100, description="Top N products", ge=1, le=10000),
    start_date: date | None = Query(None, description="Start date for filtering"),
    end_date: date | None = Query(None, description="End date for filtering"),
    current_user: User = Depends(get_current_user),
    service: AnalyticsService = Depends(get_analytics_service),
):
    performance_data = service.get_product_performance(limit, start_date, end_date)

    def data_generator() -> Iterator[dict[str, Any]]:
        for p in performance_data.products:
            yield {
                "Product ID": p.product_id,
                "Product Name": p.product_name,
                "Quantity Sold": p.quantity_sold,
                "Revenue": str(p.revenue),
                "Revenue Share (%)": str(p.revenue_share),
            }

    headers = [
        "Product ID",
        "Product Name",
        "Quantity Sold",
        "Revenue",
        "Revenue Share (%)",
    ]
    return stream_csv_response(headers, data_generator(), "product_performance.csv")


@router.get("/categories/performance", response_model=CategoryPerformanceResponse)
def get_category_performance(
    limit: int = Query(10, description="Top N categories", ge=1, le=100),
    start_date: date | None = Query(None, description="Start date for filtering"),
    end_date: date | None = Query(None, description="End date for filtering"),
    current_user: User = Depends(get_current_user),
    service: AnalyticsService = Depends(get_analytics_service),
):
    performance_data = service.get_category_performance(limit, start_date, end_date)

    return CategoryPerformanceResponse(
        categories=[
            CategoryPerformanceItem(
                category_id=c.category_id,
                category_name=c.category_name,
                quantity_sold=c.quantity_sold,
                revenue=c.revenue,
                revenue_share=c.revenue_share,
            )
            for c in performance_data.categories
        ]
    )


@router.get("/categories/performance/export")
def export_category_performance(
    limit: int = Query(100, description="Top N categories", ge=1, le=10000),
    start_date: date | None = Query(None, description="Start date for filtering"),
    end_date: date | None = Query(None, description="End date for filtering"),
    current_user: User = Depends(get_current_user),
    service: AnalyticsService = Depends(get_analytics_service),
):
    performance_data = service.get_category_performance(limit, start_date, end_date)

    def data_generator() -> Iterator[dict[str, Any]]:
        for c in performance_data.categories:
            yield {
                "Category ID": c.category_id if c.category_id else "N/A",
                "Category Name": c.category_name,
                "Quantity Sold": c.quantity_sold,
                "Revenue": str(c.revenue),
                "Revenue Share (%)": str(c.revenue_share),
            }

    headers = [
        "Category ID",
        "Category Name",
        "Quantity Sold",
        "Revenue",
        "Revenue Share (%)",
    ]
    return stream_csv_response(headers, data_generator(), "category_performance.csv")
