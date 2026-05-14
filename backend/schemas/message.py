from pydantic import BaseModel, ConfigDict
from datetime import datetime
from enum import Enum


class RoleEnum(Enum):
    user = "user"
    assistant = "assistant"


class SMessageAdd(BaseModel):
    message: str


class SMessage(SMessageAdd):
    id: int
    role: RoleEnum
    date: datetime

    model_config = ConfigDict(from_attributes=True)