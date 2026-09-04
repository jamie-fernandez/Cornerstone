import pytest

from app.database import init_db, shutdown_db


@pytest.fixture()
def db(tmp_path):
    """Initialize the database against a temporary file for test isolation."""
    db_path = str(tmp_path / "test.db")
    init_db(db_path)
    yield db_path
    shutdown_db()
