from logging.config import fileConfig
from pathlib import Path
import os
import sys

from alembic import context
from sqlalchemy import create_engine, pool
from dotenv import load_dotenv

# --------------------------------------------------
# Ensure backend/ is on PYTHONPATH
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR))

# --------------------------------------------------
# Load .env explicitly from backend/
# --------------------------------------------------
env_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set. Check backend/.env")

# --------------------------------------------------
# Alembic config
# --------------------------------------------------
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --------------------------------------------------
# Import metadata
# --------------------------------------------------
from app.database import Base
from app import models  # noqa: F401 (ensures models are registered)

target_metadata = Base.metadata

# --------------------------------------------------
# Offline migrations
# --------------------------------------------------
def run_migrations_offline() -> None:
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


# --------------------------------------------------
# Online migrations
# --------------------------------------------------
def run_migrations_online() -> None:
    engine = create_engine(
        DATABASE_URL,
        poolclass=pool.NullPool,
    )

    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


# --------------------------------------------------
# Entrypoint
# --------------------------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
