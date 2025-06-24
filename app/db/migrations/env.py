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