from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_admin_user, get_user_or_404
from app.core.security import hash_password
from app.db.database import get_db
from app.models.branch import Branch
from app.models.user import User
from app.repositories import user_repository
from app.schemas.user import UserCreate, UserResponse, UserUpdate

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    dependencies=[Depends(get_admin_user)],
)


@router.post("", response_model=UserResponse)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
):
    existing_user = user_repository.get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Email already exists",
        )

    default_branch = db.query(Branch).first()
    if not default_branch:
        default_branch = Branch(name="Main Branch")
        db.add(default_branch)
        db.flush()

    new_user = User(
        full_name=user.full_name,
        email=user.email,
        hashed_password=hash_password(user.password),
        branch_id=default_branch.id,
    )

    return user_repository.create_user(db, new_user)


@router.get("", response_model=list[UserResponse])
def get_users(
    db: Session = Depends(get_db),
):
    return user_repository.get_all_users(db)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
):
    return get_user_or_404(user_id, db)


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user: UserUpdate,
    db: Session = Depends(get_db),
):
    db_user = get_user_or_404(user_id, db)

    existing_user = user_repository.get_user_by_email(db, user.email)

    if existing_user and existing_user.id != user_id:
        raise HTTPException(
            status_code=409,
            detail="Email already exists",
        )

    db_user.full_name = user.full_name
    db_user.email = user.email

    return user_repository.update_user(db, db_user)


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
):
    user = get_user_or_404(user_id, db)

    user_repository.delete_user(db, user)

    return {"message": "User deleted"}
