import datetime

from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.repositories import sale_repository
from app.services.analytics.types import (
    CategoryPerformance,
    CategoryPerformanceResult,
    ProductPerformance,
    ProductPerformanceResult,
    SalesTrend,
    SalesTrendPoint,
    SummaryMetrics,
)


class AnalyticsService:
    def __init__(self, db: Session) -> None:
        self._db = db

    def _get_target_user_id(self, current_user: User) -> int | None:
        if current_user.role == UserRole.SALESPERSON:
            return current_user.id
        return None

    def get_summary_metrics(
        self,
        current_user: User,
        start_date: datetime.date | None = None,
        end_date: datetime.date | None = None,
    ) -> SummaryMetrics:
        user_id = self._get_target_user_id(current_user)
        data = sale_repository.get_summary_metrics(
            self._db, start_date, end_date, user_id
        )
        return SummaryMetrics(
            total_sales=data["total_sales"],
            total_transactions=data["total_transactions"],
            average_order_value=data["average_order_value"],
            highest_sale=data["highest_sale"],
            lowest_sale=data["lowest_sale"],
            average_daily_sales=data["average_daily_sales"],
            sold_products_count=data["sold_products_count"],
        )

    def get_sales_trend(
        self,
        current_user: User,
        period: str,
        start_date: datetime.date | None = None,
        end_date: datetime.date | None = None,
    ) -> SalesTrend:
        user_id = self._get_target_user_id(current_user)
        data = sale_repository.get_sales_trend(
            self._db, period, start_date, end_date, user_id
        )
        points = [
            SalesTrendPoint(
                period=item["period"],
                revenue=item["revenue"],
                transaction_count=item["transaction_count"],
            )
            for item in data
        ]
        return SalesTrend(points=points)

    def get_product_performance(
        self,
        current_user: User,
        limit: int = 10,
        start_date: datetime.date | None = None,
        end_date: datetime.date | None = None,
    ) -> ProductPerformanceResult:
        user_id = self._get_target_user_id(current_user)
        data = sale_repository.get_product_performance(
            self._db, limit, start_date, end_date, user_id
        )
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

    def get_category_performance(
        self,
        current_user: User,
        limit: int = 10,
        start_date: datetime.date | None = None,
        end_date: datetime.date | None = None,
    ) -> CategoryPerformanceResult:
        user_id = self._get_target_user_id(current_user)
        data = sale_repository.get_category_performance(
            self._db, limit, start_date, end_date, user_id
        )
        categories = [
            CategoryPerformance(
                category_id=item["category_id"],
                category_name=item["category_name"],
                quantity_sold=item["quantity_sold"],
                revenue=item["revenue"],
                revenue_share=item["revenue_share"],
            )
            for item in data
        ]
        return CategoryPerformanceResult(categories=categories)
