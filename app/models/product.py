from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    name: str
    price: float = Field(gt=0)


class ProductCreate(ProductBase):
    pass


class ProductResponse(ProductBase):
    pass


products: dict[int, ProductCreate] = {}
