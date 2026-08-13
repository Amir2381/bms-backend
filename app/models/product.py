from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.sales import SaleItem


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    price: Mapped[float] = mapped_column()
    stock: Mapped[int] = mapped_column(default=0)

    sale_items: Mapped[list["SaleItem"]] = relationship(
        back_populates="product",
    )
