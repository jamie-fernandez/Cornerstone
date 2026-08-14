"""Shared fixtures for CLI tests."""

from __future__ import annotations

import pytest

from app.database import init_db, shutdown_db


@pytest.fixture()
def temp_db(tmp_path):
    """Fixture providing an isolated temporary database path."""
    db_file = str(tmp_path / "test_cli.db")
    init_db(db_file)
    yield db_file
    shutdown_db()
