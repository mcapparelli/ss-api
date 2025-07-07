import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")  # ej: "postgresql+asyncpg://user:pass@host/db"

ECHO = os.getenv("ENV") != "PROD"

# Engine async
engine = create_async_engine(DATABASE_URL, echo=ECHO, future=True)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

Base = declarative_base()

def create_tables():
    import asyncio
    from sqlalchemy import MetaData
    
    metadata = Base.metadata
    async def run():
        async with engine.begin() as conn:
            await conn.run_sync(metadata.create_all)
    asyncio.run(run())

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except:
            await session.rollback()
            raise
