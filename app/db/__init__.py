"""from sqlalchemy.ext.asyncio import create_async_engine

from app.models.orm.base import Base
from app.core.config import PostgresqlConfiguration

async def create_tables():
    engine = create_async_engine(PostgresqlConfiguration.DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata)

    """