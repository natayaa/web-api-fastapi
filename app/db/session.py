from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession, create_async_engine, 
    async_sessionmaker
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import QueuePool

from core.config import PostgresqlConfiguration

# DB Configuration
Base = declarative_base()

class DatabaseSessionManager:
    def __init__(self):
        self._engine = None
        self._sessionmanager = None

    def init(self, db_url: str):
        self._engine = create_async_engine(
            db_url,
            poolclass=QueuePool,
            pool_size=PostgresqlConfiguration.DATABASE_POOL_SIZE, # typically 0-30,
            max_overflow=PostgresqlConfiguration.DATABASE_MAX_OVERFLOW,
            pool_pre_ping=True, # reconnect automatically
            pool_recycle=3500, # recycle connection every hour
            echo=PostgresqlConfiguration.DATABASE_ECHO, # set into database configuration
            connect_args={
                "timeout": 30,
                "server_settings": {
                    "application_name": "app"
                }
            }
        )
        self._sessionmanager = async_sessionmaker(
            bind=self._engine,
            autoflush=False,
            expire_on_commit=False,
            class_=AsyncSession
        )

    async def close(self):
        if self._engine is not None:
            await self._engine.dispose()
            self._engine = None
            self._sessionmanager = None


    @asynccontextmanager
    async def connect(self) -> AsyncGenerator[AsyncSession, None]:
        if self._engine is None:
            raise Exception("[Postgresql Error] - DatabaseSessionManager is not initialized")
        
        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        if self._sessionmanager is None:
            raise Exception("[Postgresql Error] - DatabaseSessionmanager is not initialized")

        session = self._sessionmanager()
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise
        finally:
            await session.close()

    # for testing with pytest-asyncio
    async def create_all(self):
        """Create all tables (for testing)"""
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_all(self):
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)


# Global session manager
session_manager = DatabaseSessionManager()

# FastAPI dependencies
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with session_manager.session() as session:
        yield session