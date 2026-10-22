from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SystemAlertResponse(BaseModel):
    id: int
    branch_id: int | None
    type: str
    message: str
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
