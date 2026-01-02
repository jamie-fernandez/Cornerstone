import logging
import os

from platformdirs import user_data_dir
from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import sessionmaker

import app.models  # noqa: F401 — ensures models are known to Base
from app.base import Base
from app.config import CONFIG

logger = logging.getLogger(__name__)
metadata = MetaData()
db_name = f"{CONFIG['NAME']}.db"


def get_db_path():
    """Get database path based on environment"""
    if CONFIG["DEBUG"]:
        db_dir = os.path.join(os.path.dirname(__file__), "db")
        os.makedirs(db_dir, exist_ok=True)
        return os.path.join(db_dir, db_name)
    else:
        app_name = CONFIG["NAME"]
        data_dir = user_data_dir(app_name, appauthor=False)
        os.makedirs(data_dir, exist_ok=True)
        return os.path.join(data_dir, db_name)


def init_db():
    """Initialize database connection"""
    try:
        db_path = get_db_path()
        logger.info(f"Initializing database at: {db_path}")

        engine = create_engine(f"sqlite:///{db_path}")
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        # Create all tables
        Base.metadata.create_all(bind=engine)

        return engine, SessionLocal
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


# Initialize database
engine, SessionLocal = init_db()


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        db.close()
