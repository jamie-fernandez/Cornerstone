import pytest

from app.database import init_db, shutdown_db


@pytest.fixture()
def db(tmp_path):
    """Initialize the database against a temporary file for test isolation."""
    init_db(str(tmp_path / "test.db"))
    yield
    shutdown_db()
