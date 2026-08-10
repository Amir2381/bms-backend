from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.product import Product
    from app.models.user import User


class Sale(Base):
    __tablename__ = "sales"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column()
    unit_price: Mapped[float] = mapped_column()
    sale_date: Mapped[datetime] = mapped_column()
    created_at: Mapped[datetime] = mapped_column()

    user: Mapped["User"] = relationship(
        back_populates="sales",
    )
    product: Mapped["Product"] = relationship(
        back_populates="sales",
    )
