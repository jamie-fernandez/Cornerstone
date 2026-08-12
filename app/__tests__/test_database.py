import pytest
from sqlalchemy import text

from app.database import get_session, init_db, shutdown_db


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
