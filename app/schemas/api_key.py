from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class APIKeyCreate(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    scopes: list[str] = Field(default_factory=list)
    expires_at: datetime | None = None


class APIKeyResponse(BaseModel):
    id: int
    name: str
    key: str
    scopes: list[str]
    expires_at: datetime | None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
