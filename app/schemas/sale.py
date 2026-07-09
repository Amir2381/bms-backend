from pydantic import BaseModel, ConfigDict


class SaleCreate(BaseModel):
    user_id: int
    product_id: int
    quantity: int


class SaleResponse(BaseModel):
    id: int
    product_id: int
    quantity: int

    model_config = ConfigDict(from_attributes=True)
