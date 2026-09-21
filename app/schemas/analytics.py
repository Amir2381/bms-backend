from datetime import date
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel


class SummaryMetricsResponse(BaseModel):
    total_sales: Decimal
    total_transactions: int
    average_order_value: Decimal
    highest_sale: Optional[Decimal]
    lowest_sale: Optional[Decimal]
    average_daily_sales: Decimal
    sold_products_count: int


class SalesTrendItem(BaseModel):
    date: date
    revenue: Decimal
    transaction_count: int


class SalesTrendResponse(BaseModel):
    trends: List[SalesTrendItem]


class ProductPerformanceItem(BaseModel):
    product_id: int
    product_name: str
    quantity_sold: int
    revenue: Decimal
    revenue_share: Decimal


class ProductPerformanceResponse(BaseModel):
    products: List[ProductPerformanceItem]


class CategoryPerformanceItem(BaseModel):
    category_id: Optional[int]
    category_name: str
    quantity_sold: int
    revenue: Decimal
    revenue_share: Decimal


class CategoryPerformanceResponse(BaseModel):
    categories: List[CategoryPerformanceItem]
