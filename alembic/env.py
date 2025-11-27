from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

from pathlib import Path
import sys
import os

#impostanto configuração do meu env:
from src.database.modelConfig.configPostGre import PostGreParamBuilder
from sqlalchemy import create_engine
from alembic import context
from logging.config import fileConfig

#Adiciona a raiz do projeto AO sys.path (Variaveis de ambiente)
sys.path.append(str(Path(__file__).resolve().parent.parent))

# param_builder = PostGreParamBuilder()
# config_data = param_builder.build_data_env()
# sqlAlchemy_database_url = f"postgresql://{config_data['user']}:{config_data['password']}@{config_data['host']}:{config_data['port']}/{config_data['database']}"



param_builder = PostGreParamBuilder()
config_data = param_builder.build_url_env()
print(config_data)
sqlAlchemy_database_url = config_data

config = context.config
fileConfig(config.config_file_name)
target_metadata = None





# if config.config_file_name is not None:
#     fileConfig(config.config_file_name)

# target_metadata = None


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=sqlAlchemy_database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = create_engine(
        sqlAlchemy_database_url,
        poolclass=pool.NullPool,
    )

    # connectable = engine_from_config(
    #     config.get_section(config.config_ini_section, {}),
    #     prefix="sqlalchemy.",
    #     poolclass=pool.NullPool,
    # )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
