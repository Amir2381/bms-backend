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
from app.schemas.user import UserCreate, UserResponse, UserUpdate

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
            status_code=409,
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


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
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
    current_user: User = Depends(get_current_user),
):
    user = get_user_or_404(user_id, db)

    user_repository.delete_user(db, user)

    return {"message": "User deleted"}
