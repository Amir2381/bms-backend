from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_admin_user, get_category_or_404
from app.db.database import get_db
from app.models.category import Category
from app.repositories import category_repository
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate

router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
    dependencies=[Depends(get_admin_user)],
)


@router.post("", response_model=CategoryResponse)
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
):
    existing_category = category_repository.get_category_by_name(db, category.name)
    if existing_category:
        raise HTTPException(
            status_code=409,
            detail="Category with this name already exists",
        )

    new_category = Category(name=category.name)
    return category_repository.create_category(db, new_category)


@router.get("", response_model=list[CategoryResponse])
def get_categories(
    db: Session = Depends(get_db),
):
    return category_repository.get_all_categories(db)


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
):
    return get_category_or_404(category_id, db)


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    category: CategoryUpdate,
    db: Session = Depends(get_db),
):
    db_category = get_category_or_404(category_id, db)

    existing_category = category_repository.get_category_by_name(db, category.name)
    if existing_category and existing_category.id != category_id:
        raise HTTPException(
            status_code=409,
            detail="Category with this name already exists",
        )

    db_category.name = category.name
    return category_repository.update_category(db, db_category)


@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
):
    db_category = get_category_or_404(category_id, db)
    category_repository.delete_category(db, db_category)
    return {"message": "Category deleted"}
