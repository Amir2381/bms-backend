from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base


class user(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column()
