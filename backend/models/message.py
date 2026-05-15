from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Enum
from datetime import datetime
from schemas.message import RoleEnum
from database import Model


class MessageOrm(Model):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int]
    role: Mapped[str] = mapped_column(Enum(RoleEnum))
    message: Mapped[str]
    date: Mapped[datetime]