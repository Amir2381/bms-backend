from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import (
    get_sale_or_404,
)
from app.services import sale_service
from app.core.security import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.repositories import sale_repository
from app.schemas.sale import SaleCreate, SaleResponse
from app.services.exceptions import (
    InsufficientStockError,
    ProductNotFoundError,
    UserNotFoundError,
)

router = APIRouter(
    prefix="/sales",
    tags=["Sales"],
)


@router.post("", response_model=SaleResponse)
def create_sale(
    sale: SaleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return sale_service.create_sale(db, sale)
    except UserNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ProductNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except InsufficientStockError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("", response_model=list[SaleResponse])
def get_all_sales(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return sale_repository.get_all_sales(db)


@router.get("/{sale_id}", response_model=SaleResponse)
def get_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_sale_or_404(sale_id, db)


@router.delete("/{sale_id}")
def delete_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sale = get_sale_or_404(sale_id, db)
    sale_repository.delete_sale(db, sale)

    return {
        "message": "Sale deleted",
    }
