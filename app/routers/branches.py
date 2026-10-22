from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_admin_user
from app.db.database import get_db
from app.repositories import branch_repository
from app.schemas.branch import BranchCreate, BranchResponse, BranchUpdate

router = APIRouter(
    prefix="/branches",
    tags=["Branches"],
    dependencies=[Depends(get_admin_user)],
)


@router.post("", response_model=BranchResponse)
def create_branch(
    branch: BranchCreate,
    db: Session = Depends(get_db),
):
    existing_branch = branch_repository.get_branch_by_name(db, branch.name)
    if existing_branch:
        raise HTTPException(
            status_code=409,
            detail="Branch with this name already exists",
        )
    return branch_repository.create_branch(db, branch)


@router.get("", response_model=list[BranchResponse])
def get_branches(
    db: Session = Depends(get_db),
):
    return branch_repository.get_all_branches(db)


@router.get("/{branch_id}", response_model=BranchResponse)
def get_branch(
    branch_id: int,
    db: Session = Depends(get_db),
):
    db_branch = branch_repository.get_branch(db, branch_id)
    if not db_branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    return db_branch


@router.put("/{branch_id}", response_model=BranchResponse)
def update_branch(
    branch_id: int,
    branch_in: BranchUpdate,
    db: Session = Depends(get_db),
):
    db_branch = branch_repository.get_branch(db, branch_id)
    if not db_branch:
        raise HTTPException(status_code=404, detail="Branch not found")

    existing_branch = branch_repository.get_branch_by_name(db, branch_in.name)
    if existing_branch and existing_branch.id != branch_id:
        raise HTTPException(
            status_code=409,
            detail="Branch with this name already exists",
        )

    return branch_repository.update_branch(db, db_branch, branch_in)


@router.delete("/{branch_id}")
def delete_branch(
    branch_id: int,
    db: Session = Depends(get_db),
):
    db_branch = branch_repository.get_branch(db, branch_id)
    if not db_branch:
        raise HTTPException(status_code=404, detail="Branch not found")

    branch_repository.delete_branch(db, db_branch)
    return {"message": "Branch deleted"}
