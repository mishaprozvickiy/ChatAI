from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from config import DB_URL

engine = create_async_engine(DB_URL)
new_session = async_sessionmaker(engine, expire_on_commit=False)


class Model(DeclarativeBase):
    ...


async def create_tables():
    async with engine.begin() as connection:
        await connection.run_sync(Model.metadata.create_all)

async def drop_tables():
    async with engine.begin() as connection:
        await connection.run_sync(Model.metadata.drop_all)