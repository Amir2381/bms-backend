from pydantic import BaseModel, ConfigDict, Field

from app.schemas.category import CategoryResponse


class ProductBase(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    price: float = Field(gt=0)
    stock: int = Field(ge=0)
    category_id: int | None = None


class ProductCreate(ProductBase):
    pass


class ProductResponse(ProductBase):
    id: int
    category: CategoryResponse | None = None

    model_config = ConfigDict(from_attributes=True)
