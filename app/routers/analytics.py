from datetime import date
from typing import Any, Iterator

from fastapi import (
    APIRouter,
    Depends,
    Query,
    Request,
    BackgroundTasks,
)
from sqlalchemy.orm import Session
from fastapi_cache.decorator import cache

from app.core.cache import branch_key_builder
from app.core.dependencies import get_admin_user
from app.core.rate_limit import limiter
from app.core.security import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.analytics import (
    CategoryPerformanceItem,
    CategoryPerformanceResponse,
    CrossSellingResponse,
    CrossSellRecommendation,
    CustomerPerformanceItem,
    CustomerPerformanceResponse,
    DashboardResponse,
    InventoryAlertItem,
    InventoryAlertResponse,
    ProductCrossSellItem,
    ProductPerformanceItem,
    ProductPerformanceResponse,
    SalespersonPerformanceItem,
    SalespersonPerformanceResponse,
    SalesTrendItem,
    SalesTrendResponse,
    SummaryMetricsResponse,
    ChartDataset,
    ChartResponse,
    SalesVisualizationsResponse,
)
from app.services.analytics.service import AnalyticsService

from app.schemas.analytics import (
    RFMCustomerItem,
    RFMSegmentationResponse,
    SalesForecastItem,
    SalesForecastResponse,
    InsightItem,
    ProactiveInsightsResponse,
    BranchComparisonItem,
    BranchComparisonResponse,
)
from app.worker.tasks import generate_report_task

router = APIRouter(prefix="/analytics", tags=["analytics"])


def get_analytics_service(db: Session = Depends(get_db)) -> AnalyticsService:
    return AnalyticsService(db)


@router.get("/metrics", response_model=SummaryMetricsResponse)
@limiter.limit("20/minute")
def get_summary_metrics(
    request: Request,
    start_date: date | None = Query(None, description="Start date for filtering"),
    end_date: date | None = Query(None, description="End date for filtering"),
    branch_id: int | None = Query(
        None, description="Filter by specific branch ID (Admin only)"
    ),
    current_user: User = Depends(get_current_user),
    service: AnalyticsService = Depends(get_analytics_service),
):
    return service.get_summary_metrics(current_user, start_date, end_date, branch_id)


@router.get("/trends", response_model=SalesTrendResponse)
@limiter.limit("20/minute")
def get_sales_trends(
    request: Request,
    period: str = Query("daily", description="Time period for the trend"),
    start_date: date | None = Query(None, description="Start date for filtering"),
    end_date: date | None = Query(None, description="End date for filtering"),
    branch_id: int | None = Query(
        None, description="Filter by specific branch ID (Admin only)"
    ),
    current_user: User = Depends(get_current_user),
    service: AnalyticsService = Depends(get_analytics_service),
):
    trend_data = service.get_sales_trend(
        current_user, period, start_date, end_date, branch_id
    )

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
@limiter.limit("20/minute")
def export_sales_trends(
    request: Request,
    period: str = Query("daily", description="Time period for the trend"),
    start_date: date | None = Query(None, description="Start date for filtering"),
    end_date: date | None = Query(None, description="End date for filtering"),
    branch_id: int | None = Query(
        None, description="Filter by specific branch ID (Admin only)"
    ),
    export_format: str = Query(
        "csv", pattern="^(csv|excel)$", description="Export format"
    ),
    current_user: User = Depends(get_current_user),
):
    params = {
        "period": period,
        "start_date": start_date.isoformat() if start_date else None,
        "end_date": end_date.isoformat() if end_date else None,
        "branch_id": branch_id,
        "export_format": export_format,
    }
    task = generate_report_task.delay("sales_trends", current_user.id, params)
    return {"job_id": task.id, "message": "Report generation started."}


@router.get("/products/performance", response_model=ProductPerformanceResponse)
@limiter.limit("20/minute")
def get_product_performance(
    request: Request,
    limit: int = Query(10, description="Top N products", ge=1, le=100),
    start_date: date | None = Query(None, description="Start date for filtering"),
    end_date: date | None = Query(None, description="End date for filtering"),
    branch_id: int | None = Query(
        None, description="Filter by specific branch ID (Admin only)"
    ),
    current_user: User = Depends(get_current_user),
    service: AnalyticsService = Depends(get_analytics_service),
):
    performance_data = service.get_product_performance(
        current_user, limit, start_date, end_date, branch_id
    )

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
@limiter.limit("20/minute")
def export_product_performance(
    request: Request,
    limit: int = Query(100, description="Top N products", ge=1, le=10000),
    start_date: date | None = Query(None, description="Start date for filtering"),
    end_date: date | None = Query(None, description="End date for filtering"),
    branch_id: int | None = Query(
        None, description="Filter by specific branch ID (Admin only)"
    ),
    export_format: str = Query(
        "csv", pattern="^(csv|excel)$", description="Export format"
    ),
    current_user: User = Depends(get_current_user),
):
    params = {
        "limit": limit,
        "start_date": start_date.isoformat() if start_date else None,
        "end_date": end_date.isoformat() if end_date else None,
        "branch_id": branch_id,
        "export_format": export_format,
    }
    task = generate_report_task.delay("product_performance", current_user.id, params)
    return {"job_id": task.id, "message": "Report generation started."}


@router.get("/categories/performance", response_model=CategoryPerformanceResponse)
@limiter.limit("20/minute")
def get_category_performance(
    request: Request,
    limit: int = Query(10, description="Top N categories", ge=1, le=100),
    start_date: date | None = Query(None, description="Start date for filtering"),
    end_date: date | None = Query(None, description="End date for filtering"),
    branch_id: int | None = Query(
        None, description="Filter by specific branch ID (Admin only)"
    ),
    current_user: User = Depends(get_current_user),
    service: AnalyticsService = Depends(get_analytics_service),
):
    performance_data = service.get_category_performance(
        current_user, limit, start_date, end_date, branch_id
    )

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
@limiter.limit("20/minute")
def export_category_performance(
    request: Request,
    limit: int = Query(100, description="Top N categories", ge=1, le=10000),
    start_date: date | None = Query(None, description="Start date for filtering"),
    end_date: date | None = Query(None, description="End date for filtering"),
    branch_id: int | None = Query(
        None, description="Filter by specific branch ID (Admin only)"
    ),
    export_format: str = Query(
        "csv", pattern="^(csv|excel)$", description="Export format"
    ),
    current_user: User = Depends(get_current_user),
):
    params = {
        "limit": limit,
        "start_date": start_date.isoformat() if start_date else None,
        "end_date": end_date.isoformat() if end_date else None,
        "branch_id": branch_id,
        "export_format": export_format,
    }
    task = generate_report_task.delay("category_performance", current_user.id, params)
    return {"job_id": task.id, "message": "Report generation started."}


@router.get("/salespersons/performance", response_model=SalespersonPerformanceResponse)
@limiter.limit("20/minute")
def get_salesperson_performance(
    request: Request,
    limit: int = Query(10, description="Top N salespersons", ge=1, le=100),
    start_date: date | None = Query(None, description="Start date for filtering"),
    end_date: date | None = Query(None, description="End date for filtering"),
    branch_id: int | None = Query(
        None, description="Filter by specific branch ID (Admin only)"
    ),
    current_user: User = Depends(get_admin_user),
    service: AnalyticsService = Depends(get_analytics_service),
):
    performance_data = service.get_salesperson_performance(
        current_user, limit, start_date, end_date, branch_id
    )

    return SalespersonPerformanceResponse(
        salespersons=[
            SalespersonPerformanceItem(
                user_id=sp.user_id,
                user_name=sp.user_name,
                quantity_sold=sp.quantity_sold,
                revenue=sp.revenue,
                transaction_count=sp.transaction_count,
            )
            for sp in performance_data.salespersons
        ]
    )


@router.get("/customers/top", response_model=CustomerPerformanceResponse)
@limiter.limit("20/minute")
def get_top_customers(
    request: Request,
    limit: int = Query(10, description="Top N customers", ge=1, le=100),
    start_date: date | None = Query(None, description="Start date for filtering"),
    end_date: date | None = Query(None, description="End date for filtering"),
    branch_id: int | None = Query(
        None, description="Filter by specific branch ID (Admin only)"
    ),
    current_user: User = Depends(get_current_user),
    service: AnalyticsService = Depends(get_analytics_service),
):
    performance_data = service.get_top_customers(
        current_user, limit, start_date, end_date, branch_id
    )

    return CustomerPerformanceResponse(
        customers=[
            CustomerPerformanceItem(
                customer_id=c.customer_id,
                customer_name=c.customer_name,
                customer_phone=c.customer_phone,
                revenue=c.revenue,
                profit=c.profit,
                transaction_count=c.transaction_count,
            )
            for c in performance_data.customers
        ]
    )


@router.get("/customers/top/export")
@limiter.limit("20/minute")
def export_top_customers(
    request: Request,
    limit: int = Query(100, description="Top N customers", ge=1, le=10000),
    start_date: date | None = Query(None, description="Start date for filtering"),
    end_date: date | None = Query(None, description="End date for filtering"),
    branch_id: int | None = Query(
        None, description="Filter by specific branch ID (Admin only)"
    ),
    export_format: str = Query(
        "csv", pattern="^(csv|excel)$", description="Export format"
    ),
    current_user: User = Depends(get_current_user),
):
    params = {
        "limit": limit,
        "start_date": start_date.isoformat() if start_date else None,
        "end_date": end_date.isoformat() if end_date else None,
        "branch_id": branch_id,
        "export_format": export_format,
    }
    task = generate_report_task.delay("top_customers", current_user.id, params)
    return {"job_id": task.id, "message": "Report generation started."}


@router.get("/cross-selling", response_model=CrossSellingResponse)
@limiter.limit("20/minute")
def get_cross_selling(
    request: Request,
    product_id: int | None = Query(
        None, description="Filter recommendations for a specific product"
    ),
    limit_per_product: int = Query(
        3, description="Number of recommendations per product"
    ),
    branch_id: int | None = Query(
        None, description="Filter by specific branch ID (Admin only)"
    ),
    current_user: User = Depends(get_current_user),
    service: AnalyticsService = Depends(get_analytics_service),
):
    result = service.get_cross_selling(
        current_user, product_id, limit_per_product, branch_id
    )

    return CrossSellingResponse(
        items=[
            ProductCrossSellItem(
                product_id=item.product_id,
                product_name=item.product_name,
                recommendations=[
                    CrossSellRecommendation(
                        product_id=rec.product_id,
                        product_name=rec.product_name,
                        frequency=rec.frequency,
                    )
                    for rec in item.recommendations
                ],
            )
            for item in result.items
        ]
    )


@router.get("/inventory-alerts", response_model=InventoryAlertResponse)
@limiter.limit("20/minute")
def get_inventory_alerts(
    request: Request,
    days_threshold: int = Query(7, description="Threshold in days to trigger an alert"),
    lookback_days: int = Query(
        30, description="Lookback period in days for daily run rate calculation"
    ),
    branch_id: int | None = Query(
        None, description="Filter by specific branch ID (Admin only)"
    ),
    current_user: User = Depends(get_current_user),
    service: AnalyticsService = Depends(get_analytics_service),
):
    result = service.get_inventory_alerts(
        current_user, days_threshold, lookback_days, branch_id
    )

    return InventoryAlertResponse(
        alerts=[
            InventoryAlertItem(
                product_id=alert.product_id,
                product_name=alert.product_name,
                current_stock=alert.current_stock,
                daily_run_rate=alert.daily_run_rate,
                days_remaining=alert.days_remaining,
            )
            for alert in result.alerts
        ]
    )


@router.get("/dashboard", response_model=DashboardResponse)
@limiter.limit("20/minute")
@cache(expire=300, namespace="dashboard", key_builder=branch_key_builder)
def get_dashboard_data(
    request: Request,
    period: str = Query("daily", description="Time period for the trend"),
    start_date: date | None = Query(None, description="Start date for filtering"),
    end_date: date | None = Query(None, description="End date for filtering"),
    branch_id: int | None = Query(
        None, description="Filter by specific branch ID (Admin only)"
    ),
    current_user: User = Depends(get_current_user),
    service: AnalyticsService = Depends(get_analytics_service),
):
    metrics_data = service.get_summary_metrics(
        current_user, start_date, end_date, branch_id
    )
    metrics_response = SummaryMetricsResponse(
        total_sales=metrics_data.total_sales,
        total_profit=metrics_data.total_profit,
        profit_margin=metrics_data.profit_margin,
        total_transactions=metrics_data.total_transactions,
        average_order_value=metrics_data.average_order_value,
        highest_sale=metrics_data.highest_sale,
        lowest_sale=metrics_data.lowest_sale,
        average_daily_sales=metrics_data.average_daily_sales,
        sold_products_count=metrics_data.sold_products_count,
        average_clv=metrics_data.average_clv,
    )

    trend_data = service.get_sales_trend(
        current_user, period, start_date, end_date, branch_id
    )
    trends_response = SalesTrendResponse(
        trends=[
            SalesTrendItem(
                date=point.period,
                revenue=point.revenue,
                transaction_count=point.transaction_count,
            )
            for point in trend_data.points
        ]
    )

    product_data = service.get_product_performance(
        current_user,
        limit=5,
        start_date=start_date,
        end_date=end_date,
        branch_id=branch_id,
    )
    products_response = ProductPerformanceResponse(
        products=[
            ProductPerformanceItem(
                product_id=p.product_id,
                product_name=p.product_name,
                quantity_sold=p.quantity_sold,
                revenue=p.revenue,
                revenue_share=p.revenue_share,
            )
            for p in product_data.products
        ]
    )

    return DashboardResponse(
        metrics=metrics_response,
        trends=trends_response,
        top_products=products_response,
    )


@router.get("/dashboard/export")
@limiter.limit("20/minute")
def export_dashboard(
    request: Request,
    start_date: date | None = Query(None, description="Start date for filtering"),
    end_date: date | None = Query(None, description="End date for filtering"),
    branch_id: int | None = Query(
        None, description="Filter by specific branch ID (Admin only)"
    ),
    current_user: User = Depends(get_current_user),
):
    params = {
        "start_date": start_date.isoformat() if start_date else None,
        "end_date": end_date.isoformat() if end_date else None,
        "branch_id": branch_id,
    }
    task = generate_report_task.delay("dashboard", current_user.id, params)
    return {"job_id": task.id, "message": "Report generation started."}


@router.get(
    "/visualizations/sales-distribution", response_model=SalesVisualizationsResponse
)
@limiter.limit("20/minute")
def get_sales_visualizations(
    request: Request,
    start_date: date | None = Query(None, description="Start date for filtering"),
    end_date: date | None = Query(None, description="End date for filtering"),
    branch_id: int | None = Query(
        None, description="Filter by specific branch ID (Admin only)"
    ),
    current_user: User = Depends(get_current_user),
    service: AnalyticsService = Depends(get_analytics_service),
):
    trend_data = service.get_sales_trend(
        current_user,
        period="daily",
        start_date=start_date,
        end_date=end_date,
        branch_id=branch_id,
    )
    trend_labels = [point.period.isoformat() for point in trend_data.points]
    trend_revenue = [point.revenue for point in trend_data.points]

    trend_chart = ChartResponse(
        labels=trend_labels,
        datasets=[ChartDataset(label="Revenue", data=trend_revenue)],
    )

    category_data = service.get_category_performance(
        current_user,
        limit=10,
        start_date=start_date,
        end_date=end_date,
        branch_id=branch_id,
    )
    cat_labels = [c.category_name for c in category_data.categories]
    cat_revenue = [c.revenue for c in category_data.categories]

    cat_chart = ChartResponse(
        labels=cat_labels,
        datasets=[ChartDataset(label="Revenue by Category", data=cat_revenue)],
    )

    return SalesVisualizationsResponse(
        sales_trend=trend_chart, category_distribution=cat_chart
    )


@router.get("/customers/rfm", response_model=RFMSegmentationResponse)
@limiter.limit("20/minute")
def get_rfm_segmentation(
    request: Request,
    limit: int = Query(100, description="Top N customers to segment", ge=1, le=1000),
    branch_id: int | None = Query(
        None, description="Filter by specific branch ID (Admin only)"
    ),
    current_user: User = Depends(get_current_user),
    service: AnalyticsService = Depends(get_analytics_service),
):
    result = service.get_rfm_segmentation(current_user, limit, branch_id)

    return RFMSegmentationResponse(
        customers=[
            RFMCustomerItem(
                customer_id=c.customer_id,
                customer_name=c.customer_name,
                customer_phone=c.customer_phone,
                recency_days=c.recency_days,
                frequency=c.frequency,
                monetary=c.monetary,
                segment=c.segment,
            )
            for c in result.customers
        ]
    )


@router.get("/forecast", response_model=SalesForecastResponse)
@limiter.limit("20/minute")
@cache(expire=43200, namespace="forecast", key_builder=branch_key_builder)
def get_sales_forecast(
    request: Request,
    days: int = Query(7, description="Number of days to forecast", ge=1, le=30),
    branch_id: int | None = Query(
        None, description="Filter by specific branch ID (Admin only)"
    ),
    current_user: User = Depends(get_current_user),
    service: AnalyticsService = Depends(get_analytics_service),
):
    forecast_data = service.get_sales_forecast(current_user, days, branch_id)

    return SalesForecastResponse(
        forecasts=[
            SalesForecastItem(
                date=f.date,
                expected_revenue=f.expected_revenue,
            )
            for f in forecast_data.forecasts
        ]
    )


@router.get("/insights", response_model=ProactiveInsightsResponse)
@limiter.limit("20/minute")
def get_proactive_insights(
    request: Request,
    branch_id: int | None = Query(
        None, description="Filter by specific branch ID (Admin only)"
    ),
    current_user: User = Depends(get_current_user),
    service: AnalyticsService = Depends(get_analytics_service),
):
    result = service.get_proactive_insights(current_user, branch_id)

    return ProactiveInsightsResponse(
        insights=[
            InsightItem(
                type=i.type,
                message=i.message,
            )
            for i in result.insights
        ]
    )


@router.get("/branches/compare", response_model=BranchComparisonResponse)
@limiter.limit("10/minute")
def compare_branches(
    request: Request,
    current_user: User = Depends(get_admin_user),
    service: AnalyticsService = Depends(get_analytics_service),
):
    result = service.compare_branches(current_user)

    return BranchComparisonResponse(
        comparisons=[
            BranchComparisonItem(
                branch_id=c.branch_id,
                branch_name=c.branch_name,
                current_month_revenue=c.current_month_revenue,
                previous_month_revenue=c.previous_month_revenue,
                revenue_growth_percent=c.revenue_growth_percent,
                current_month_profit=c.current_month_profit,
                previous_month_profit=c.previous_month_profit,
                profit_growth_percent=c.profit_growth_percent,
                current_month_transactions=c.current_month_transactions,
                previous_month_transactions=c.previous_month_transactions,
                transaction_growth_percent=c.transaction_growth_percent,
            )
            for c in result.comparisons
        ]
    )
