import os
import sys
from logging.config import fileConfig

from alembic import context
from flask import Flask
from sqlalchemy import engine_from_config, pool

# ensure backend package root is on sys.path so `app` can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import Config
from app.extensions import db
import app.models  # noqa: F401  register all models

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Build a minimal app carrying only the SQLAlchemy config so migrations are
# decoupled from external services (e.g. TMDB / Redis).
config_app = Flask(__name__)
config_app.config.from_object(Config)
db.init_app(config_app)
target_metadata = db.metadata
config.set_main_option("sqlalchemy.url", config_app.config["SQLALCHEMY_DATABASE_URI"])


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()