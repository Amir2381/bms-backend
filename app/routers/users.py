from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_user_or_404
from app.core.security import (
    get_current_user,
    hash_password,
)
from app.models.user import User
from app.db.database import get_db
from app.repositories import user_repository
from app.schemas.user import UserCreate, UserResponse

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.post("", response_model=UserResponse)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
):

    existing_user = user_repository.get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(
            status_code=401,
            detail="Email already exists",
        )

    new_user = User(
        full_name=user.full_name,
        email=user.email,
        hashed_password=hash_password(user.password),
    )

    return user_repository.create_user(db, new_user)


@router.get("", response_model=list[UserResponse])
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return user_repository.get_all_users(db)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_or_404(user_id, db)
