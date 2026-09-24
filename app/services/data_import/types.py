from dataclasses import dataclass
from datetime import datetime
from typing import TypedDict


class RawImportRow(TypedDict, total=False):
    date: str
    product: str
    quantity: str
    unit_price: str
    cost_price: str
    seller: str
    customer_phone: str
    category: str


class CleanImportRow(TypedDict, total=False):
    date: datetime
    product: str
    quantity: int
    unit_price: float
    cost_price: float | None
    seller: str
    customer_phone: str
    category: str


@dataclass
class ParsedImportData:
    headers: list[str]
    rows: list[RawImportRow]


@dataclass
class ImportedSaleInput:
    sale_date: datetime
    product: str
    quantity: int
    unit_price: float
    cost_price: float | None = None
    seller: str = ""
    customer_phone: str = ""
    category: str = ""
