from pydantic import BaseModel, Field


class SaleCreate(BaseModel):
    product_id: int
    quantity: int


class Sale(BaseModel):
    id: int
    product_id: int
    quantity: int
    date: str


sales: dict[int, Sale] = {}
