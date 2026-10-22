from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.branch import Branch
from app.schemas.branch import BranchCreate, BranchUpdate


def create_branch(db: Session, branch_in: BranchCreate) -> Branch:
    new_branch = Branch(
        name=branch_in.name,
        location=branch_in.location,
    )
    db.add(new_branch)
    db.commit()
    db.refresh(new_branch)
    return new_branch


def get_branch(db: Session, branch_id: int) -> Branch | None:
    stmt = select(Branch).where(Branch.id == branch_id)
    return db.scalars(stmt).first()


def get_branch_by_name(db: Session, name: str) -> Branch | None:
    stmt = select(Branch).where(Branch.name == name)
    return db.scalars(stmt).first()


def get_all_branches(db: Session) -> list[Branch]:
    stmt = select(Branch).order_by(Branch.name)
    return list(db.scalars(stmt).all())


def update_branch(db: Session, db_branch: Branch, branch_in: BranchUpdate) -> Branch:
    db_branch.name = branch_in.name
    db_branch.location = branch_in.location
    db.commit()
    db.refresh(db_branch)
    return db_branch


def delete_branch(db: Session, db_branch: Branch) -> None:
    db.delete(db_branch)
    db.commit()
