from sqlalchemy.orm import Session

from app.repositories import sale_repository
from app.services.analytics.types import (
    ProductPerformance,
    ProductPerformanceResult,
    SalesTrend,
    SalesTrendPoint,
    SummaryMetrics,
)


class AnalyticsService:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_summary_metrics(self) -> SummaryMetrics:
        data = sale_repository.get_summary_metrics(self._db)
        return SummaryMetrics(
            total_sales=data["total_sales"],
            total_transactions=data["total_transactions"],
            average_order_value=data["average_order_value"],
            highest_sale=data["highest_sale"],
            lowest_sale=data["lowest_sale"],
            average_daily_sales=data["average_daily_sales"],
            sold_products_count=data["sold_products_count"],
        )

    def get_sales_trend(self, period: str) -> SalesTrend:
        data = sale_repository.get_sales_trend(self._db, period)
        points = [
            SalesTrendPoint(
                period=item["period"],
                revenue=item["revenue"],
                transaction_count=item["transaction_count"],
            )
            for item in data
        ]
        return SalesTrend(points=points)

    def get_product_performance(self, limit: int = 10) -> ProductPerformanceResult:
        data = sale_repository.get_product_performance(self._db, limit)
        products = [
            ProductPerformance(
                product_id=item["product_id"],
                product_name=item["product_name"],
                quantity_sold=item["quantity_sold"],
                revenue=item["revenue"],
                revenue_share=item["revenue_share"],
            )
            for item in data
        ]
        return ProductPerformanceResult(products=products)
