from pydantic import BaseModel, ConfigDict, Field


class BranchBase(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    location: str | None = None


class BranchCreate(BranchBase):
    pass


class BranchUpdate(BranchBase):
    pass


class BranchResponse(BranchBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
