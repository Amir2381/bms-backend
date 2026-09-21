from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.analytics import (
    SalesTrendItem,
    SalesTrendResponse,
    SummaryMetricsResponse,
)
from app.services.analytics.service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/metrics", response_model=SummaryMetricsResponse)
def get_summary_metrics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = AnalyticsService(db)
    return service.get_summary_metrics()


@router.get("/trends", response_model=SalesTrendResponse)
def get_sales_trends(
    period: str = Query("daily", description="Time period for the trend"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = AnalyticsService(db)
    trend_data = service.get_sales_trend(period)

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
