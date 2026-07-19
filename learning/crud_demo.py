from sqlalchemy import select
from app.db.database import SessionLocal
from app.models.user import User

db = SessionLocal()

# new_user = User(full_name="Amir", email="Amir@gmail.com")
# db.add(new_user)
# db.commit()
# db.refresh(new_user)
# print(new_user.id)

# stmt = select(User).where(User.id == 5)
# user = db.scalars(stmt).first()
# if user:
#     user.full_name = "Abbas"
#     user.email = "Abbas@gmail.com"

#     db.commit()
#     db.refresh(user)

#     print(user.id, user.full_name, user.email)

stmt = select(User).where(User.id == 5)
user = db.scalars(stmt).first()
if user:
    db.delete(user)
    db.commit()
    print("user deleted!")
