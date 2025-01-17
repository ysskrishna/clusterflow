from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from src.core.config import Config


engine = create_async_engine(Config.DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, expire_on_commit=False, bind=engine, class_=AsyncSession)
Base = declarative_base()

async def get_db():
    async with SessionLocal() as session:
        yield session