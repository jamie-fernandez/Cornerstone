import logging
import os
from contextlib import contextmanager

from platformdirs import user_data_dir
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

import app.models  # noqa: F401 — ensures models are known to Base
from app.base import Base
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

        # check_same_thread=False: pywebview invokes JS-API methods on
        # background threads, so connections must be usable across threads.
        engine = create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False},
        )
        event.listen(engine, "connect", _set_sqlite_pragma)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        # Create all tables
        Base.metadata.create_all(bind=engine)

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
