from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.sales import SaleItem
    from app.models.category import Category


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    price: Mapped[float] = mapped_column()
    cost_price: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)
    stock: Mapped[int] = mapped_column(default=0)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"))

    category: Mapped["Category | None"] = relationship(
        back_populates="products",
    )
    sale_items: Mapped[list["SaleItem"]] = relationship(
        back_populates="product",
    )
