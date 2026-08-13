from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.product import ProductResponse
from app.schemas.user import UserResponse


class SaleItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class SaleItemResponse(BaseModel):
    id: int
    product: ProductResponse
    quantity: int
    unit_price: float

    model_config = ConfigDict(from_attributes=True)


class SaleCreate(BaseModel):
    user_id: int
    items: list[SaleItemCreate]


class SaleResponse(BaseModel):
    id: int
    user: UserResponse
    items: list[SaleItemResponse]
    sale_date: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
