"""
Alembic async env.py — AsyncSQLAlchemy + postgresql+asyncpg compatible configuration.

This file should be FULLY replaced in the `alembic/env.py` created by
the `alembic init alembic` command.
"""
import asyncio
import sys
import os
from pathlib import Path


# ── PATH FIX ─────────────────────────────────────────────────────────────────
# Alembic runs this file from the alembic/ directory.
# We add the project root (evograph-api/) to sys.path so Python can find the 'app' package.
_project_root = str(Path(__file__).resolve().parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)
# ─────────────────────────────────────────────────────────────────────────────

from logging.config import fileConfig

from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context

# ── APPLICATION IMPORTS ────────────────────────────────────────────────────
from app.db.database import Base  
import app.db.models  

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


target_metadata = Base.metadata

# ── DATABASE URL ─────────────────────────────────────────────────────────
from dotenv import load_dotenv         
load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]  


def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,         
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations():
  
    connectable = create_async_engine(DATABASE_URL)
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online():
    asyncio.run(run_async_migrations())


def run_migrations_offline():
   
    url = DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
