import datetime

from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.repositories import sale_repository
from app.services.analytics.types import (
    CategoryPerformance,
    CategoryPerformanceResult,
    CrossSellingResult,
    CrossSellRecommendation,
    InventoryAlert,
    InventoryAlertResult,
    ProductCrossSell,
    ProductPerformance,
    ProductPerformanceResult,
    SalespersonPerformance,
    SalespersonPerformanceResult,
    CustomerPerformance,
    CustomerPerformanceResult,
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
            total_profit=data["total_profit"],
            profit_margin=data["profit_margin"],
            total_transactions=data["total_transactions"],
            average_order_value=data["average_order_value"],
            highest_sale=data["highest_sale"],
            lowest_sale=data["lowest_sale"],
            average_daily_sales=data["average_daily_sales"],
            sold_products_count=data["sold_products_count"],
            average_clv=data["average_clv"],
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

    def get_salesperson_performance(
        self,
        limit: int = 10,
        start_date: datetime.date | None = None,
        end_date: datetime.date | None = None,
    ) -> SalespersonPerformanceResult:
        data = sale_repository.get_salesperson_performance(
            self._db, limit, start_date, end_date
        )
        salespersons = [
            SalespersonPerformance(
                user_id=item["user_id"],
                user_name=item["user_name"],
                quantity_sold=item["quantity_sold"],
                revenue=item["revenue"],
                transaction_count=item["transaction_count"],
            )
            for item in data
        ]
        return SalespersonPerformanceResult(salespersons=salespersons)

    def get_top_customers(
        self,
        current_user: User,
        limit: int = 10,
        start_date: datetime.date | None = None,
        end_date: datetime.date | None = None,
    ) -> CustomerPerformanceResult:
        user_id = self._get_target_user_id(current_user)
        data = sale_repository.get_top_customers(
            self._db, limit, start_date, end_date, user_id
        )
        customers = [
            CustomerPerformance(
                customer_id=item["customer_id"],
                customer_name=item["customer_name"],
                customer_phone=item["customer_phone"],
                revenue=item["revenue"],
                profit=item["profit"],
                transaction_count=item["transaction_count"],
            )
            for item in data
        ]
        return CustomerPerformanceResult(customers=customers)

    def get_cross_selling(
        self,
        current_user: User,
        product_id: int | None = None,
        limit_per_product: int = 3,
    ) -> CrossSellingResult:
        user_id = self._get_target_user_id(current_user)
        data = sale_repository.get_cross_selling_products(
            self._db, limit_per_product, product_id, user_id
        )

        items = [
            ProductCrossSell(
                product_id=item["product_id"],
                product_name=item["product_name"],
                recommendations=[
                    CrossSellRecommendation(
                        product_id=rec["product_id"],
                        product_name=rec["product_name"],
                        frequency=rec["frequency"],
                    )
                    for rec in item["recommendations"]
                ],
            )
            for item in data
        ]
        return CrossSellingResult(items=items)

    def get_inventory_alerts(
        self,
        current_user: User,
        days_threshold: int = 7,
        lookback_days: int = 30,
    ) -> InventoryAlertResult:
        user_id = self._get_target_user_id(current_user)
        data = sale_repository.get_inventory_alerts(
            self._db, days_threshold, lookback_days, user_id
        )

        alerts = [
            InventoryAlert(
                product_id=item["product_id"],
                product_name=item["product_name"],
                current_stock=item["current_stock"],
                daily_run_rate=item["daily_run_rate"],
                days_remaining=item["days_remaining"],
            )
            for item in data
        ]
        return InventoryAlertResult(alerts=alerts)
