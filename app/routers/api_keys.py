from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_admin_user
from app.db.database import get_db
from app.repositories import api_key_repository
from app.schemas.api_key import APIKeyCreate, APIKeyResponse

router = APIRouter(
    prefix="/api-keys",
    tags=["API Keys"],
    dependencies=[Depends(get_admin_user)],
)


@router.post("", response_model=APIKeyResponse)
def create_key(
    key_in: APIKeyCreate,
    db: Session = Depends(get_db),
):
    return api_key_repository.create_api_key(db, key_in)


@router.get("", response_model=list[APIKeyResponse])
def get_keys(
    db: Session = Depends(get_db),
):
    return api_key_repository.get_all_api_keys(db)


@router.post("/{key_id}/revoke", response_model=APIKeyResponse)
def revoke_key(
    key_id: int,
    db: Session = Depends(get_db),
):
    key_record = api_key_repository.get_api_key_by_id(db, key_id)
    if not key_record:
        raise HTTPException(status_code=404, detail="API Key not found")

    return api_key_repository.revoke_api_key(db, key_record)
