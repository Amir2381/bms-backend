from app.db.database import Base, engine

from app.models.user import User
from app.models.product import Product
from app.models.sales import Sale

Base.metadata.create_all(bind=engine)

print("Tables created successfully.")
