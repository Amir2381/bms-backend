from pydantic import BaseModel, ConfigDict

from app.schemas.product import ProductResponse
from app.schemas.user import UserResponse


class SaleCreate(BaseModel):
    user_id: int
    product_id: int
    quantity: int


class SaleResponse(BaseModel):
    id: int
    product: ProductResponse
    user: UserResponse
    quantity: int

    model_config = ConfigDict(from_attributes=True)
