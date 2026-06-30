from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column()
