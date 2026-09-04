import logging
import os
import sys
from contextlib import contextmanager

from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from platformdirs import user_data_dir
from sqlalchemy import create_engine, event, pool
from sqlalchemy.orm import sessionmaker

import app.models  # noqa: F401 — ensures models are known to Base
from app.config import CONFIG

logger = logging.getLogger(__name__)
db_name = f"{CONFIG['NAME']}.db"

# Populated by init_db(), which is called explicitly at app startup (start.py)
# rather than at import time, so importing this module has no side effects, and
# tests can initialize against a temporary database.
engine = None
SessionLocal = None


def get_db_path():
    """Get a database path based on the environment"""
    if CONFIG["DEBUG"]:
        db_dir = os.path.join(os.path.dirname(__file__), "db")
        os.makedirs(db_dir, exist_ok=True)
        return os.path.join(db_dir, db_name)
    else:
        app_name = CONFIG["NAME"]
        data_dir = user_data_dir(app_name, appauthor=False)
        os.makedirs(data_dir, exist_ok=True)
        return os.path.join(data_dir, db_name)


def get_alembic_config(db_path: str | None = None) -> Config:
    """Build Alembic Config pointing to project or frozen bundle paths."""
    if getattr(sys, "frozen", False):
        base_dir = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    else:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    ini_path = os.path.join(base_dir, "alembic.ini")
    migrations_path = os.path.join(base_dir, "app", "migrations")

    if os.path.exists(ini_path):
        alembic_cfg = Config(ini_path)
    else:
        alembic_cfg = Config()

    alembic_cfg.set_main_option("script_location", migrations_path)
    target_db_path = db_path or get_db_path()
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{target_db_path}")

    return alembic_cfg


def run_migrations(db_path: str | None = None, target: str = "head") -> None:
    """Run programmatic Alembic upgrade to target revision."""
    target_db_path = db_path or get_db_path()
    logger.info(f"Running database migrations to '{target}' on: {target_db_path}")
    alembic_cfg = get_alembic_config(db_path=target_db_path)
    command.upgrade(alembic_cfg, target)


def get_current_revision(db_path: str | None = None) -> str | None:
    """Inspect and return current database migration revision."""
    target_db_path = db_path or get_db_path()
    if not os.path.exists(target_db_path):
        return None

    temp_engine = create_engine(
        f"sqlite:///{target_db_path}",
        poolclass=pool.NullPool,
        connect_args={"check_same_thread": False},
    )
    try:
        with temp_engine.connect() as conn:
            ctx = MigrationContext.configure(conn)
            return ctx.get_current_revision()
    except Exception as e:  # noqa: BLE001 - inspection fallback
        logger.debug(f"Could not inspect migration revision: {e}")
        return None
    finally:
        temp_engine.dispose()


def _set_sqlite_pragma(dbapi_connection, _connection_record):
    """Harden SQLite: enforce foreign keys (off by default) and use WAL."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.close()


def init_db(db_path=None):
    """Initialize the database connection. Call once at app startup.

    Accepts an optional ``db_path`` so tests can use a temporary database.
    """
    global engine, SessionLocal
    if SessionLocal is not None:
        return engine, SessionLocal
    try:
        db_path = db_path or get_db_path()
        logger.info(f"Initializing database at: {db_path}")

        # Ensure parent directory exists
        db_dir = os.path.dirname(os.path.abspath(db_path))
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)

        # Run migrations to ensure latest schema is applied
        run_migrations(db_path=db_path, target="head")

        # check_same_thread=False: pywebview invokes JS-API methods on
        # background threads, so connections must be usable across threads.
        engine = create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False},
        )
        event.listen(engine, "connect", _set_sqlite_pragma)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        return engine, SessionLocal
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


def shutdown_db():
    """Dispose of the engine and reset module state (app exit and tests)."""
    global engine, SessionLocal
    if engine is not None:
        engine.dispose()
    engine = None
    SessionLocal = None


@contextmanager
def get_session():
    """Provide a transactional session using the session-per-call pattern.

    pywebview has no request lifecycle like FastAPI, so each bridge call
    manages its own session with commit/rollback semantics.
    """
    if SessionLocal is None:
        raise RuntimeError("Database not initialized — call init_db() first")
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
