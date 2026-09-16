from sqlalchemy.orm import Session

from app.services.analytics.types import (
    ProductPerformanceResult,
    SalesTrend,
    SummaryMetrics,
)


class AnalyticsService:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_summary_metrics(self) -> SummaryMetrics:
        raise NotImplementedError

    def get_sales_trend(self, period: str) -> SalesTrend:
        raise NotImplementedError

    def get_product_performance(self) -> ProductPerformanceResult:
        raise NotImplementedError
