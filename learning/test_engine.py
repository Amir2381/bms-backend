from sqlalchemy import create_engine

DATABASE_URL = "postgresql+psycopg://postgres:1122@localhost:5432/bms_db"

engine = create_engine(DATABASE_URL, echo=True)
with engine.connect():
    print("connected successfully!")
