from pydantic import BaseModel


class SaleCreate(BaseModel):
    user_id: int
    product_id: int
    quantity: int


class SaleResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
