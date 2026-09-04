import os

import pytest
from sqlalchemy import text

from app.database import (
    get_alembic_config,
    get_current_revision,
    get_session,
    init_db,
    run_migrations,
    shutdown_db,
)


class TestDatabase:
    def test_init_is_idempotent(self, db):
        engine_a, session_a = init_db()
        engine_b, session_b = init_db()

        assert engine_a is engine_b
        assert session_a is session_b

    def test_get_session_executes_queries(self, db):
        with get_session() as session:
            assert session.execute(text("SELECT 1")).scalar() == 1

    def test_foreign_keys_pragma_enabled(self, db):
        with get_session() as session:
            assert session.execute(text("PRAGMA foreign_keys")).scalar() == 1

    def test_get_session_rolls_back_on_error(self, db):
        with pytest.raises(ValueError, match="boom"), get_session() as session:
            session.execute(text("SELECT 1"))
            raise ValueError("boom")

    def test_get_session_requires_init(self, db):
        shutdown_db()

        with pytest.raises(RuntimeError, match="init_db"), get_session():
            pass

    def test_get_alembic_config_custom_path(self, tmp_path):
        db_path = str(tmp_path / "custom.db")
        config = get_alembic_config(db_path=db_path)
        assert config.get_main_option("sqlalchemy.url") == f"sqlite:///{db_path}"
        assert config.get_main_option("script_location") is not None
        assert config.get_main_option("script_location").endswith(
            os.path.join("app", "migrations")
        )

    def test_get_current_revision_after_init(self, db):
        rev = get_current_revision(db)
        assert rev is not None
        assert isinstance(rev, str)
        assert rev == "0001"

    def test_get_current_revision_non_existent(self, tmp_path):
        non_existent_path = str(tmp_path / "does_not_exist.db")
        assert get_current_revision(non_existent_path) is None

    def test_run_migrations_explicit(self, tmp_path):
        custom_db = str(tmp_path / "explicit.db")
        run_migrations(db_path=custom_db, target="head")
        rev = get_current_revision(db_path=custom_db)
        assert rev == "0001"
