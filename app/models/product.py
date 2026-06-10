from pydantic import BaseModel, Field


class Product(BaseModel):
    name: str
    price: float


products = {}
