from datetime import date, timedelta
from decimal import Decimal

from fastapi import APIRouter, Depends
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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    today = date.today()
    return SalesTrendResponse(
        trends=[
            SalesTrendItem(date=today - timedelta(days=2), revenue=Decimal("4500.0")),
            SalesTrendItem(date=today - timedelta(days=1), revenue=Decimal("6200.0")),
            SalesTrendItem(date=today, revenue=Decimal("8100.0")),
        ]
    )
