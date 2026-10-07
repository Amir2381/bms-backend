from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class SummaryMetrics:
    total_sales: Decimal
    total_profit: Decimal
    profit_margin: Decimal
    total_transactions: int
    average_order_value: Decimal
    highest_sale: Decimal | None
    lowest_sale: Decimal | None
    average_daily_sales: Decimal
    sold_products_count: int
    average_clv: Decimal


@dataclass(frozen=True)
class SalesTrendPoint:
    period: date
    revenue: Decimal
    transaction_count: int


@dataclass(frozen=True)
class SalesTrend:
    points: list[SalesTrendPoint]


@dataclass(frozen=True)
class ProductPerformance:
    product_id: int
    product_name: str
    quantity_sold: int
    revenue: Decimal
    revenue_share: Decimal


@dataclass(frozen=True)
class ProductPerformanceResult:
    products: list[ProductPerformance]


@dataclass(frozen=True)
class CategoryPerformance:
    category_id: int | None
    category_name: str
    quantity_sold: int
    revenue: Decimal
    revenue_share: Decimal


@dataclass(frozen=True)
class CategoryPerformanceResult:
    categories: list[CategoryPerformance]


@dataclass(frozen=True)
class SalespersonPerformance:
    user_id: int
    user_name: str
    quantity_sold: int
    revenue: Decimal
    transaction_count: int


@dataclass(frozen=True)
class SalespersonPerformanceResult:
    salespersons: list[SalespersonPerformance]


@dataclass(frozen=True)
class CustomerPerformance:
    customer_id: int
    customer_name: str
    customer_phone: str
    revenue: Decimal
    profit: Decimal
    transaction_count: int


@dataclass(frozen=True)
class CustomerPerformanceResult:
    customers: list[CustomerPerformance]


@dataclass(frozen=True)
class CrossSellRecommendation:
    product_id: int
    product_name: str
    frequency: int


@dataclass(frozen=True)
class ProductCrossSell:
    product_id: int
    product_name: str
    recommendations: list[CrossSellRecommendation]


@dataclass(frozen=True)
class CrossSellingResult:
    items: list[ProductCrossSell]


@dataclass(frozen=True)
class InventoryAlert:
    product_id: int
    product_name: str
    current_stock: int
    daily_run_rate: Decimal
    days_remaining: Decimal | None


@dataclass(frozen=True)
class InventoryAlertResult:
    alerts: list[InventoryAlert]


@dataclass(frozen=True)
class RFMCustomer:
    customer_id: int
    customer_name: str
    customer_phone: str
    recency_days: int
    frequency: int
    monetary: Decimal
    segment: str


@dataclass(frozen=True)
class RFMSegmentationResult:
    customers: list[RFMCustomer]


@dataclass(frozen=True)
class SalesForecastPoint:
    date: date
    expected_revenue: Decimal


@dataclass(frozen=True)
class SalesForecast:
    forecasts: list[SalesForecastPoint]


@dataclass(frozen=True)
class InsightMessage:
    type: str
    message: str


@dataclass(frozen=True)
class ProactiveInsightsResult:
    insights: list[InsightMessage]


@dataclass(frozen=True)
class BranchComparison:
    branch_id: int
    branch_name: str
    current_month_revenue: Decimal
    previous_month_revenue: Decimal
    revenue_growth_percent: Decimal
    current_month_profit: Decimal
    previous_month_profit: Decimal
    profit_growth_percent: Decimal
    current_month_transactions: int
    previous_month_transactions: int
    transaction_growth_percent: Decimal


@dataclass(frozen=True)
class BranchComparisonResult:
    comparisons: list[BranchComparison]
