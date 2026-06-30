from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = "postgresql+psycopg://postgres:1122@localhost:5432/bms_db"

engine = create_engine(DATABASE_URL, echo=True)


class Base(DeclarativeBase):
    pass


sessionlocal = sessionmaker(bind=engine)


def get_db():
    db = sessionlocal()
    try:
        yield db
    finally:
        db.close()
