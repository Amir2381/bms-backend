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


class SalesTrendResponse(BaseModel):
    trends: List[SalesTrendItem]
