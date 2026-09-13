from datetime import datetime
from typing import TypedDict


class RawImportRow(TypedDict, total=False):
    date: str
    product: str
    quantity: str
    unit_price: str
    seller: str


class CleanImportRow(TypedDict, total=False):
    date: datetime
    product: str
    quantity: int
    unit_price: float
    seller: str
