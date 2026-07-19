from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql+psycopg://postgres:1122@localhost:5432/bms_db"

engine = create_engine(DATABASE_URL, echo=True)

with engine.begin() as conn:
    conn.execute(text("""
    CREATE TABLE IF NOT EXISTS test_table(
                      id SERIAL PRIMARY KEY,
                      name VARCHAR(100)
    )
    """))
    conn.execute(text("""
    INSERT INTO test_table(name)
    VALUES('Amir')
    """))
