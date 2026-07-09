from pydantic import BaseModel, Field, ConfigDict


class ProductBase(BaseModel):
    name: str
    price: float = Field(gt=0)
    stock: int


class ProductCreate(ProductBase):
    pass


class ProductResponse(ProductBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
