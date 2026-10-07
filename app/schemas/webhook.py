from datetime import datetime

from pydantic import BaseModel, ConfigDict, HttpUrl


class WebhookCreate(BaseModel):
    url: HttpUrl


class WebhookResponse(BaseModel):
    id: int
    url: HttpUrl
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
