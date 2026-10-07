import datetime
from decimal import Decimal
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
    BranchComparison,
    BranchComparisonResult,
)

from app.services.analytics.types import (
    RFMCustomer,
    RFMSegmentationResult,
    SalesForecast,
    SalesForecastPoint,
    InsightMessage,
    ProactiveInsightsResult,
)


class AnalyticsService:
    def __init__(self, db: Session) -> None:
        self._db = db

    def _get_target_branch_id(
        self, current_user: User, requested_branch_id: int | None = None
    ) -> int | None:
        if current_user.role == UserRole.SALESPERSON:
            return current_user.branch_id
        return requested_branch_id

    def get_summary_metrics(
        self,
        current_user: User,
        start_date: datetime.date | None = None,
        end_date: datetime.date | None = None,
        branch_id: int | None = None,
    ) -> SummaryMetrics:
        target_branch_id = self._get_target_branch_id(current_user, branch_id)
        data = sale_repository.get_summary_metrics(
            self._db, start_date, end_date, target_branch_id
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
        branch_id: int | None = None,
    ) -> SalesTrend:
        target_branch_id = self._get_target_branch_id(current_user, branch_id)
        data = sale_repository.get_sales_trend(
            self._db, period, start_date, end_date, target_branch_id
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
        branch_id: int | None = None,
    ) -> ProductPerformanceResult:
        target_branch_id = self._get_target_branch_id(current_user, branch_id)
        data = sale_repository.get_product_performance(
            self._db, limit, start_date, end_date, target_branch_id
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
        branch_id: int | None = None,
    ) -> CategoryPerformanceResult:
        target_branch_id = self._get_target_branch_id(current_user, branch_id)
        data = sale_repository.get_category_performance(
            self._db, limit, start_date, end_date, target_branch_id
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
        current_user: User,
        limit: int = 10,
        start_date: datetime.date | None = None,
        end_date: datetime.date | None = None,
        branch_id: int | None = None,
    ) -> SalespersonPerformanceResult:
        target_branch_id = self._get_target_branch_id(current_user, branch_id)
        data = sale_repository.get_salesperson_performance(
            self._db, limit, start_date, end_date, target_branch_id
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
        branch_id: int | None = None,
    ) -> CustomerPerformanceResult:
        target_branch_id = self._get_target_branch_id(current_user, branch_id)
        data = sale_repository.get_top_customers(
            self._db, limit, start_date, end_date, target_branch_id
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
        branch_id: int | None = None,
    ) -> CrossSellingResult:
        target_branch_id = self._get_target_branch_id(current_user, branch_id)
        data = sale_repository.get_cross_selling_products(
            self._db, limit_per_product, product_id, target_branch_id
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
        branch_id: int | None = None,
    ) -> InventoryAlertResult:
        target_branch_id = self._get_target_branch_id(current_user, branch_id)
        data = sale_repository.get_inventory_alerts(
            self._db, days_threshold, lookback_days, target_branch_id
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

    def get_rfm_segmentation(
        self,
        current_user: User,
        limit: int = 100,
        branch_id: int | None = None,
    ) -> RFMSegmentationResult:
        target_branch_id = self._get_target_branch_id(current_user, branch_id)
        data = sale_repository.get_rfm_data(self._db, limit, target_branch_id)

        customers = []
        for item in data:
            r = item["recency_days"]
            f = item["frequency"]
            m = item["monetary"]

            segment = "Regular"
            if r <= 30 and f >= 5 and m >= 1000:
                segment = "VIP"
            elif r <= 60 and f >= 3:
                segment = "Loyal"
            elif r > 90 and f < 2:
                segment = "At Risk"
            elif r > 60:
                segment = "Needs Attention"

            customers.append(
                RFMCustomer(
                    customer_id=item["customer_id"],
                    customer_name=item["customer_name"],
                    customer_phone=item["customer_phone"],
                    recency_days=r,
                    frequency=f,
                    monetary=m,
                    segment=segment,
                )
            )

        return RFMSegmentationResult(customers=customers)

    def get_sales_forecast(
        self,
        current_user: User,
        days_to_predict: int = 7,
        branch_id: int | None = None,
    ) -> SalesForecast:
        target_branch_id = self._get_target_branch_id(current_user, branch_id)

        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=30)

        trend_data = self.get_sales_trend(
            current_user=current_user,
            period="daily",
            start_date=start_date,
            end_date=end_date,
            branch_id=target_branch_id,
        )

        revenues = [float(point.revenue) for point in trend_data.points]

        if not revenues:
            return SalesForecast(forecasts=[])

        forecasts = []
        current_date = end_date
        window_size = 5

        working_revenues = revenues.copy()

        for _ in range(days_to_predict):
            current_date += datetime.timedelta(days=1)

            recent = working_revenues[-window_size:]
            n = len(recent)

            if n == 0:
                predicted = 0.0
            else:
                weights = list(range(1, n + 1))
                total_weight = sum(weights)
                predicted = sum(r * w for r, w in zip(recent, weights)) / total_weight

            working_revenues.append(predicted)
            forecasts.append(
                SalesForecastPoint(
                    date=current_date,
                    expected_revenue=Decimal(round(predicted, 2)),
                )
            )

        return SalesForecast(forecasts=forecasts)

    def get_proactive_insights(
        self,
        current_user: User,
        branch_id: int | None = None,
    ) -> ProactiveInsightsResult:
        insights = []
        target_branch_id = self._get_target_branch_id(current_user, branch_id)

        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=14)

        trend_data = self.get_sales_trend(
            current_user=current_user,
            period="daily",
            start_date=start_date,
            end_date=end_date,
            branch_id=target_branch_id,
        )

        curr_week_start = end_date - datetime.timedelta(days=7)
        prev_week_revenue = 0.0
        curr_week_revenue = 0.0

        for point in trend_data.points:
            if point.period > curr_week_start:
                curr_week_revenue += float(point.revenue)
            else:
                prev_week_revenue += float(point.revenue)

        if prev_week_revenue > 0:
            drop_ratio = (prev_week_revenue - curr_week_revenue) / prev_week_revenue
            if drop_ratio >= 0.20:
                percentage = round(drop_ratio * 100)
                insights.append(
                    InsightMessage(
                        type="WARNING",
                        message=f"Sales have dropped by {percentage}% in the last 7 days compared to the previous week.",
                    )
                )

        inventory_alerts = self.get_inventory_alerts(
            current_user=current_user,
            days_threshold=3,
            lookback_days=30,
            branch_id=target_branch_id,
        )

        for alert in inventory_alerts.alerts:
            if alert.current_stock == 0:
                insights.append(
                    InsightMessage(
                        type="CRITICAL",
                        message=f"Product '{alert.product_name}' is out of stock!",
                    )
                )
            elif alert.days_remaining is not None:
                insights.append(
                    InsightMessage(
                        type="WARNING",
                        message=f"Product '{alert.product_name}' will run out in ~{round(alert.days_remaining)} days.",
                    )
                )

        if not insights:
            insights.append(
                InsightMessage(
                    type="INFO",
                    message="All metrics are stable. No immediate action required.",
                )
            )

        return ProactiveInsightsResult(insights=insights)

    def compare_branches(
        self,
        current_user: User,
    ) -> BranchComparisonResult:
        if current_user.role != UserRole.ADMIN:
            return BranchComparisonResult(comparisons=[])

        data = sale_repository.compare_branches(self._db)

        comparisons = []
        for item in data:
            prev_rev = item["previous_month_revenue"]
            curr_rev = item["current_month_revenue"]
            rev_growth = (
                round(((curr_rev - prev_rev) / prev_rev) * 100, 2)
                if prev_rev > 0
                else Decimal("0.0")
            )

            prev_prof = item["previous_month_profit"]
            curr_prof = item["current_month_profit"]
            prof_growth = (
                round(((curr_prof - prev_prof) / prev_prof) * 100, 2)
                if prev_prof > 0
                else Decimal("0.0")
            )

            prev_txn = Decimal(item["previous_month_transactions"])
            curr_txn = Decimal(item["current_month_transactions"])
            txn_growth = (
                round(((curr_txn - prev_txn) / prev_txn) * 100, 2)
                if prev_txn > 0
                else Decimal("0.0")
            )

            comparisons.append(
                BranchComparison(
                    branch_id=item["branch_id"],
                    branch_name=item["branch_name"],
                    current_month_revenue=curr_rev,
                    previous_month_revenue=prev_rev,
                    revenue_growth_percent=rev_growth,
                    current_month_profit=curr_prof,
                    previous_month_profit=prev_prof,
                    profit_growth_percent=prof_growth,
                    current_month_transactions=int(curr_txn),
                    previous_month_transactions=int(prev_txn),
                    transaction_growth_percent=txn_growth,
                )
            )

        return BranchComparisonResult(comparisons=comparisons)
