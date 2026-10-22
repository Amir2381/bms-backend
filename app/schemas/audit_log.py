from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class AuditLogResponse(BaseModel):
    id: int
    user_id: int | None
    action: str
    entity_type: str
    entity_id: str | None
    details: dict[str, Any] | None
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
