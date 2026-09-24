import enum
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.sales import Sale


class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    SALESPERSON = "SALESPERSON"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str] = mapped_column()
    role: Mapped[UserRole] = mapped_column(default=UserRole.SALESPERSON)

    sales: Mapped[list["Sale"]] = relationship(
        back_populates="user",
    )
