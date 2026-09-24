from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.product import Product
    from app.models.sales import Sale
    from app.models.user import User


class Branch(Base):
    __tablename__ = "branches"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, index=True)
    location: Mapped[str | None] = mapped_column()

    users: Mapped[list["User"]] = relationship(
        back_populates="branch",
    )
    sales: Mapped[list["Sale"]] = relationship(
        back_populates="branch",
    )
