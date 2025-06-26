from logging.config import fileConfig
from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlalchemy.ext.asyncio import AsyncEngine

from app.models.orm.base import Base
#from app.core.config import 

conf = context.config
fileConfig(conf.config_file_name)

target_metadata = Base.metadata

def run_migration_offline():
    url = ""
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"}
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migration_online():
    connectable = AsyncEngine(
        engine_from_config(
            configuration=conf.get_section(conf.config_ini_section),
            prefix="sqlalchemy",
            poolclass=pool.NullPool,
            future=True
        )
    )

    async with connectable.connect() as connection:
        await connection.run_sync(
            lambda sync_con: context.configure(
                connection=sync_con,
                target_metadata=target_metadata
            )
        )
        await connection.run_sync(context.run_migrations)


if context.is_offline_mode():
    run_migration_offline()
else:
    run_migration_online()