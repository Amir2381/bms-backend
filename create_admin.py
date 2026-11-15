import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.models.user import User, UserRole
from app.models.branch import Branch
from app.models.sales import Sale, SaleItem
from app.models.product import Product
from app.models.category import Category
from app.models.customer import Customer
from app.core.security import hash_password


def setup_admin():
    db = SessionLocal()
    try:
        branch = db.query(Branch).first()
        if not branch:
            branch = Branch(name="Main Branch", location="Headquarters")
            db.add(branch)
            db.commit()
            db.refresh(branch)

        email = "admin@example.com"
        password = "admin123"

        existing_user = db.query(User).filter(User.email == email).first()

        if existing_user:
            existing_user.hashed_password = hash_password(password)
            existing_user.role = UserRole.ADMIN
            db.commit()
            print(f"Admin already existed. Password reset to: {password}")
        else:
            new_admin = User(
                full_name="System Admin",
                email=email,
                hashed_password=hash_password(password),
                role=UserRole.ADMIN,
                branch_id=branch.id,
            )
            db.add(new_admin)
            db.commit()
            print(f"Admin created successfully! Email: {email} | Password: {password}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    setup_admin()
