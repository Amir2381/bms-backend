from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.customer import Customer
from app.models.user import User
from app.repositories import customer_repository
from app.schemas.customer import CustomerCreate, CustomerResponse

router = APIRouter(
    prefix="/customers",
    tags=["Customers (CRM)"],
    dependencies=[Depends(get_current_user)],
)


@router.post("", response_model=CustomerResponse)
def create_customer(
    customer: CustomerCreate,
    db: Session = Depends(get_db),
):
    existing = customer_repository.get_customer_by_phone(db, customer.phone)
    if existing:
        raise HTTPException(
            status_code=409,
            detail="Customer with this phone number already exists",
        )

    new_customer = Customer(
        phone=customer.phone,
        full_name=customer.full_name,
    )

    return customer_repository.create_customer(db, new_customer)


@router.get("", response_model=list[CustomerResponse])
def get_customers(
    db: Session = Depends(get_db),
):
    return customer_repository.get_all_customers(db)
