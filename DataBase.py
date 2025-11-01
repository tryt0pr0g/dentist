import os
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker, DeclarativeBase


#SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://postgres:root@localhost:5432/dentist_db"
SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)
AsyncSession = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


ModelORM = Base
meta = MetaData()


async def get_session():
    async with AsyncSession() as session:
        yield session


async def setup_database():
    async with engine.begin() as conn:
        await  conn.run_sync(Base.metadata.drop_all)
        await  conn.run_sync(Base.metadata.create_all)