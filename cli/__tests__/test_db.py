from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

from alembic.config import Config
from typer.testing import CliRunner

from app.database import get_alembic_config
from cli.commands.db import get_next_revision_id
from cli.main import app

runner = CliRunner()


class TestDatabaseMigrationsCLI:
    def test_get_next_revision_id_from_empty(self, tmp_path):
        migrations_dir = tmp_path / "migrations"
        versions_dir = migrations_dir / "versions"
        versions_dir.mkdir(parents=True)

        # Create basic alembic files for ScriptDirectory to parse
        (migrations_dir / "script.py.mako").write_text(
            '"""${message}"""\nrevision = ${repr(up_revision)}\ndown_revision = ${repr(down_revision)}\n',
            encoding="utf-8",
        )
        (migrations_dir / "env.py").write_text("# env\n", encoding="utf-8")

        cfg = Config()
        cfg.set_main_option("script_location", str(migrations_dir))

        next_id = get_next_revision_id(cfg)
        assert next_id == "0001"

    def test_get_next_revision_id_sequential(self):
        cfg = get_alembic_config()
        next_id = get_next_revision_id(cfg)
        assert next_id == "0002"

    def test_get_next_revision_id_multiple_revisions(self, tmp_path):
        migrations_dir = tmp_path / "migrations"
        versions_dir = migrations_dir / "versions"
        versions_dir.mkdir(parents=True)

        (migrations_dir / "script.py.mako").write_text(
            '"""${message}"""\nrevision = ${repr(up_revision)}\ndown_revision = ${repr(down_revision)}\n',
            encoding="utf-8",
        )
        (migrations_dir / "env.py").write_text("# env\n", encoding="utf-8")

        # Create mock migration revisions 0001, 0002, 0003
        (versions_dir / "0001_initial.py").write_text(
            '"""initial"""\nrevision = "0001"\ndown_revision = None\n',
            encoding="utf-8",
        )
        (versions_dir / "0002_create_users.py").write_text(
            '"""users"""\nrevision = "0002"\ndown_revision = "0001"\n',
            encoding="utf-8",
        )
        (versions_dir / "0003_add_email.py").write_text(
            '"""email"""\nrevision = "0003"\ndown_revision = "0002"\n',
            encoding="utf-8",
        )

        cfg = Config()
        cfg.set_main_option("script_location", str(migrations_dir))

        next_id = get_next_revision_id(cfg)
        assert next_id == "0004"

    def test_db_migrate_invokes_command_with_sequential_rev_id(self, temp_db):
        mock_script = MagicMock()
        mock_script.revision = "0002"
        mock_script.path = "/app/migrations/versions/0002_add_profile.py"

        with patch(
            "cli.commands.db.command.revision", return_value=mock_script
        ) as mock_rev:
            result = runner.invoke(
                app,
                ["db", "migrate", "-m", "add_profile_table", "--db-path", temp_db],
            )
            assert result.exit_code == 0
            assert "Created migration revision: 0002" in result.stdout
            assert mock_rev.called
            call_kwargs = mock_rev.call_args[1]
            assert call_kwargs["message"] == "add_profile_table"
            assert call_kwargs["rev_id"] == "0002"

    def test_db_migrate_with_explicit_rev_id_override(self, temp_db):
        mock_script = MagicMock()
        mock_script.revision = "9999"
        mock_script.path = "/app/migrations/versions/9999_custom.py"

        with patch(
            "cli.commands.db.command.revision", return_value=mock_script
        ) as mock_rev:
            result = runner.invoke(
                app,
                [
                    "db",
                    "migrate",
                    "-m",
                    "custom_migration",
                    "--rev-id",
                    "9999",
                    "--db-path",
                    temp_db,
                ],
            )
            assert result.exit_code == 0
            assert "Created migration revision: 9999" in result.stdout
            assert mock_rev.called
            call_kwargs = mock_rev.call_args[1]
            assert call_kwargs["rev_id"] == "9999"

    def test_db_revision_alias_passes_rev_id(self, temp_db):
        mock_script = MagicMock()
        mock_script.revision = "0005"
        mock_script.path = "/app/migrations/versions/0005_alias.py"

        with patch(
            "cli.commands.db.command.revision", return_value=mock_script
        ) as mock_rev:
            result = runner.invoke(
                app,
                [
                    "db",
                    "revision",
                    "-m",
                    "alias_test",
                    "-r",
                    "0005",
                    "--db-path",
                    temp_db,
                ],
            )
            assert result.exit_code == 0
            assert "Created migration revision: 0005" in result.stdout
            assert mock_rev.called
            assert mock_rev.call_args[1]["rev_id"] == "0005"

    def test_alembic_logger_is_silenced_to_warning(self):
        import logging

        alembic_logger = logging.getLogger("alembic")
        assert alembic_logger.getEffectiveLevel() >= logging.WARNING

    def test_db_migrate_creates_sequential_file_in_temp_env(self, tmp_path):
        migrations_dir = tmp_path / "app" / "migrations"
        versions_dir = migrations_dir / "versions"
        versions_dir.mkdir(parents=True)

        mako_content = (
            '"""${message}\n\nRevision ID: ${up_revision}\nRevises: ${down_revision}\n"""\n'
            "revision: str = ${repr(up_revision)}\n"
            "down_revision = ${repr(down_revision)}\n"
            "def upgrade() -> None:\n    pass\n"
            "def downgrade() -> None:\n    pass\n"
        )
        (migrations_dir / "script.py.mako").write_text(mako_content, encoding="utf-8")
        (migrations_dir / "env.py").write_text("# env\n", encoding="utf-8")

        # Initial version 0001
        (versions_dir / "0001_initial_version.py").write_text(
            '"""initial version"""\nrevision: str = "0001"\ndown_revision = None\n',
            encoding="utf-8",
        )

        ini_file = tmp_path / "alembic.ini"
        ini_file.write_text(
            f"[alembic]\nscript_location = {migrations_dir}\nfile_template = %%(rev)s_%%(slug)s\n",
            encoding="utf-8",
        )

        cfg = Config(str(ini_file))
        cfg.set_main_option("script_location", str(migrations_dir))

        # Check next rev id computation
        next_id = get_next_revision_id(cfg)
        assert next_id == "0002"

        # Execute actual alembic revision generation
        from alembic import command

        script = command.revision(
            cfg,
            message="create users table",
            autogenerate=False,
            rev_id=next_id,
        )

        assert script is not None
        assert script.revision == "0002"
        assert os.path.exists(script.path)
        assert os.path.basename(script.path) == "0002_create_users_table.py"
