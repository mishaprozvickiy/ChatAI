from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Enum
from datetime import datetime
from schema import RoleEnum

engine = create_async_engine("sqlite+aiosqlite:///messages.db")
new_session = async_sessionmaker(engine, expire_on_commit=False)


class Model(DeclarativeBase):
    ...


class MessageOrm(Model):
    __tablename__ = "messages"
    id: Mapped[int] = mapped_column(primary_key=True)
    role: Mapped[str] = mapped_column(Enum(RoleEnum))
    message: Mapped[str]
    date: Mapped[datetime]


async def create_table():
    async with engine.begin() as connection:
        await connection.run_sync(Model.metadata.create_all)