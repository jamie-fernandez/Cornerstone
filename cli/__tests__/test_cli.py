from __future__ import annotations

import json
from unittest.mock import patch

from sqlalchemy import text
from typer.testing import CliRunner

from app.database import get_session, shutdown_db
from cli.main import app

runner = CliRunner()


class TestAppCommands:
    def test_version_command(self):
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "Cornerstone" in result.stdout
        assert "version" in result.stdout

    def test_version_json(self):
        result = runner.invoke(app, ["version", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["name"] == "Cornerstone"
        assert "version" in data
        assert "python" in data

    def test_info_command(self):
        result = runner.invoke(app, ["info"])
        assert result.exit_code == 0
        assert "Application Configuration" in result.stdout
        assert "Cornerstone" in result.stdout

    def test_info_json(self):
        result = runner.invoke(app, ["info", "-j"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["name"] == "Cornerstone"
        assert "slug" in data
        assert "db_path" in data
        assert "python_version" in data

    def test_stats_command(self):
        result = runner.invoke(app, ["stats"])
        assert result.exit_code == 0
        assert "System Information & Stats" in result.stdout
        assert "CPU Usage" in result.stdout

    def test_stats_json(self):
        result = runner.invoke(app, ["stats", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert "system" in data
        assert "stats" in data
        assert "cpu_percent" in data["stats"]

    def test_users_command(self):
        result = runner.invoke(app, ["users"])
        assert result.exit_code == 0
        assert "User Data" in result.stdout
        assert "John Doe" in result.stdout

    def test_users_json(self):
        result = runner.invoke(app, ["users", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert isinstance(data, list)
        assert len(data) >= 2
        assert data[0]["name"] == "John Doe"

    def test_dev_command(self):
        with patch("cli.commands.dev.main") as mock_dev_main:
            result = runner.invoke(app, ["dev"])
            assert result.exit_code == 0
            assert mock_dev_main.called

    def test_build_command(self):
        with patch("cli.commands.build.main") as mock_build_main:
            result = runner.invoke(app, ["build"])
            assert result.exit_code == 0
            assert mock_build_main.called

    def test_clean_command(self):
        with patch("cli.commands.clean.clean_artifacts") as mock_clean:
            result = runner.invoke(app, ["clean"])
            assert result.exit_code == 0
            assert mock_clean.called

    def test_setup_command(self):
        with patch("cli.commands.setup.setup") as mock_setup_main:
            result = runner.invoke(app, ["setup"])
            assert result.exit_code == 0
            assert mock_setup_main.called

    def test_init_command(self):
        with patch("cli.commands.init.rebrand") as mock_rebrand:
            result = runner.invoke(
                app,
                ["init", "My", "App", "--description", "Desc", "--clean-examples"],
            )
            assert result.exit_code == 0
            mock_rebrand.assert_called_once_with("My App", "Desc", True, aliases=None)

    def test_init_command_with_aliases(self):
        with patch("cli.commands.init.rebrand") as mock_rebrand:
            result = runner.invoke(
                app,
                ["init", "My", "App", "-a", "stone", "--alias", "tf"],
            )
            assert result.exit_code == 0
            mock_rebrand.assert_called_once_with(
                "My App", "", False, aliases=["stone", "tf"]
            )

    def test_cli_help_contains_workflows_and_examples(self):
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Cornerstone CLI" in result.stdout
        assert "Common Workflows" in result.stdout
        assert "docs" in result.stdout

    def test_command_helps_contain_examples(self):
        for cmd in [
            "dev",
            "build",
            "clean",
            "setup",
            "init",
            "version",
            "info",
            "stats",
            "users",
            "docs",
        ]:
            result = runner.invoke(app, [cmd, "--help"])
            assert result.exit_code == 0
            assert "Examples:" in result.stdout


class TestDbCommands:
    def test_db_help_contains_workflows_and_examples(self):
        result = runner.invoke(app, ["db", "--help"])
        assert result.exit_code == 0
        assert "Database Management" in result.stdout
        assert "Common Workflows" in result.stdout

    def test_db_subcommand_helps_contain_examples(self):
        for subcmd in ["info", "test", "init", "reset", "tables", "query"]:
            result = runner.invoke(app, ["db", subcmd, "--help"])
            assert result.exit_code == 0
            assert "Examples:" in result.stdout

    def test_db_info(self, temp_db):
        result = runner.invoke(app, ["db", "info", "--db-path", temp_db])
        assert result.exit_code == 0
        assert "Database Information" in result.stdout
        assert "File Exists" in result.stdout
        assert "Yes" in result.stdout

    def test_db_info_json(self, temp_db):
        result = runner.invoke(app, ["db", "info", "--db-path", temp_db, "--json"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["path"] == temp_db
        assert data["exists"] is True
        assert "journal_mode" in data
        assert data["foreign_keys"] is True

    def test_db_test_success(self, temp_db):
        result = runner.invoke(app, ["db", "test", "--db-path", temp_db])
        assert result.exit_code == 0
        assert "Database connection OK" in result.stdout

    def test_db_test_json(self, temp_db):
        result = runner.invoke(app, ["db", "test", "--db-path", temp_db, "-j"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["status"] == "success"

    def test_db_init(self, tmp_path):
        new_db = str(tmp_path / "new.db")
        shutdown_db()
        result = runner.invoke(app, ["db", "init", "--db-path", new_db])
        assert result.exit_code == 0
        assert "Database initialized at" in result.stdout
        shutdown_db()

    def test_db_reset_with_yes(self, temp_db):
        result = runner.invoke(app, ["db", "reset", "--yes", "--db-path", temp_db])
        assert result.exit_code == 0
        assert "Database recreated and initialized" in result.stdout

    def test_db_reset_prompt_cancel(self, temp_db):
        result = runner.invoke(app, ["db", "reset", "--db-path", temp_db], input="n\n")
        assert result.exit_code != 0
        assert "Operation cancelled" in result.stdout

    def test_db_tables_empty(self, temp_db):
        result = runner.invoke(app, ["db", "tables", "--db-path", temp_db])
        assert result.exit_code == 0
        assert "No tables found" in result.stdout

    def test_db_tables_with_schema(self, temp_db):
        with get_session() as session:
            session.execute(
                text(
                    "CREATE TABLE items (id INTEGER PRIMARY KEY, title TEXT NOT NULL, price REAL)"
                )
            )

        result = runner.invoke(app, ["db", "tables", "--db-path", temp_db])
        assert result.exit_code == 0
        assert "Table: items" in result.stdout
        assert "title" in result.stdout
        assert "price" in result.stdout

        json_res = runner.invoke(app, ["db", "tables", "--db-path", temp_db, "--json"])
        assert json_res.exit_code == 0
        data = json.loads(json_res.stdout)
        assert "items" in data
        col_names = [col["name"] for col in data["items"]]
        assert "id" in col_names
        assert "title" in col_names
        assert "price" in col_names

    def test_db_query_select(self, temp_db):
        result = runner.invoke(
            app,
            [
                "db",
                "query",
                "SELECT 42 AS answer, 'Cornerstone' AS project",
                "--db-path",
                temp_db,
            ],
        )
        assert result.exit_code == 0
        assert "42" in result.stdout
        assert "Cornerstone" in result.stdout

    def test_db_query_select_json(self, temp_db):
        result = runner.invoke(
            app,
            [
                "db",
                "query",
                "SELECT 42 AS answer, 'Cornerstone' AS project",
                "--db-path",
                temp_db,
                "--json",
            ],
        )
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data == [{"answer": 42, "project": "Cornerstone"}]

    def test_db_query_dml(self, temp_db):
        runner.invoke(
            app,
            [
                "db",
                "query",
                "CREATE TABLE logs (id INTEGER PRIMARY KEY, message TEXT)",
                "--db-path",
                temp_db,
            ],
        )
        insert_res = runner.invoke(
            app,
            [
                "db",
                "query",
                "INSERT INTO logs (message) VALUES ('test message')",
                "--db-path",
                temp_db,
            ],
        )
        assert insert_res.exit_code == 0
        assert "Query executed successfully" in insert_res.stdout

    def test_db_query_error(self, temp_db):
        result = runner.invoke(
            app,
            ["db", "query", "SELECT * FROM non_existent_table", "--db-path", temp_db],
        )
        assert result.exit_code == 1
        assert "SQL execution failed" in result.stdout
