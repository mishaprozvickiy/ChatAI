from pydantic import BaseModel, ConfigDict
from datetime import datetime


class SMessageAdd(BaseModel):
    message: str


class SMessage(SMessageAdd):
    id: int
    role: str
    date: datetime
    model_config = ConfigDict(from_attributes=True)