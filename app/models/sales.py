from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.product import Product
    from app.models.user import User


class Sale(Base):
    __tablename__ = "sales"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    sale_date: Mapped[datetime] = mapped_column()
    created_at: Mapped[datetime] = mapped_column()

    user: Mapped["User"] = relationship(
        back_populates="sales",
    )
    items: Mapped[list["SaleItem"]] = relationship(
        back_populates="sale",
        cascade="all, delete-orphan",
    )


class SaleItem(Base):
    __tablename__ = "sale_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    sale_id: Mapped[int] = mapped_column(ForeignKey("sales.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column()
    unit_price: Mapped[float] = mapped_column(Numeric(10, 2))

    sale: Mapped["Sale"] = relationship(
        back_populates="items",
    )
    product: Mapped["Product"] = relationship(
        back_populates="sale_items",
    )
