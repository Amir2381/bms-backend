from pydantic import BaseModel, ConfigDict, Field

from app.schemas.product import ProductResponse
from app.schemas.user import UserResponse


class SaleCreate(BaseModel):
    user_id: int
    product_id: int
    quantity: int = Field(gt=0)


class SaleResponse(BaseModel):
    id: int
    product: ProductResponse
    user: UserResponse
    quantity: int

    model_config = ConfigDict(from_attributes=True)
