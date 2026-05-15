from pydantic import BaseModel, ConfigDict


class SUserAdd(BaseModel):
    username: str
    password: str


class SUser(SUserAdd):
    id: int

    model_config = ConfigDict(from_attributes=True)