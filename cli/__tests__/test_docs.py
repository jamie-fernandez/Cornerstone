from __future__ import annotations

import json
from typing import Annotated

import typer
from typer.testing import CliRunner

from cli.commands.docs import (
    clear_docs_cache,
    extract_cli_metadata,
    generate_markdown_doc,
    parse_docstring,
)
from cli.main import app

runner = CliRunner()


class TestDocsCommand:
    def test_docs_overview(self):
        result = runner.invoke(app, ["docs"])
        assert result.exit_code == 0
        assert "Cornerstone CLI - Interactive Documentation" in result.stdout
        assert "Common Workflows & Quick Start" in result.stdout
        assert "Commands Catalog & Examples" in result.stdout

    def test_docs_specific_topic(self):
        for topic in [
            "dev",
            "build",
            "clean",
            "setup",
            "init",
            "version",
            "info",
            "stats",
            "users",
            "db",
            "docs",
        ]:
            result = runner.invoke(app, ["docs", topic])
            assert result.exit_code == 0
            assert topic in result.stdout.lower()
            assert "Examples" in result.stdout

    def test_docs_unknown_topic(self):
        result = runner.invoke(app, ["docs", "nonexistent_topic"])
        assert result.exit_code == 1
        assert "Unknown documentation topic" in result.stdout

    def test_docs_markdown_full(self):
        result = runner.invoke(app, ["docs", "--markdown"])
        assert result.exit_code == 0
        assert "# Cornerstone CLI Documentation" in result.stdout
        assert "## Quick Start Workflow" in result.stdout
        assert "## Commands Catalog" in result.stdout

    def test_docs_markdown_topic(self):
        result = runner.invoke(app, ["docs", "db", "-m"])
        assert result.exit_code == 0
        assert "# db - Database Management" in result.stdout
        assert "### Usage" in result.stdout
        assert "### Subcommands" in result.stdout
        assert "### Examples" in result.stdout

    def test_docs_json_full(self):
        result = runner.invoke(app, ["docs", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert "overview" in data
        assert "dev" in data
        assert "db" in data
        assert "init" in data

    def test_docs_json_topic(self):
        result = runner.invoke(app, ["docs", "init", "-j"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert "init" in data
        assert "init" in data["init"]["title"]
        assert len(data["init"]["examples"]) > 0

    def test_docs_json_unknown_topic(self):
        result = runner.invoke(app, ["docs", "unknown", "-j"])
        assert result.exit_code == 1
        data = json.loads(result.stdout)
        assert "error" in data


class TestIntrospectionEngine:
    def test_parse_docstring_empty(self):
        parsed = parse_docstring(None)
        assert parsed["description"] == ""
        assert parsed["examples"] == []
        assert parsed["notes"] is None

    def test_parse_docstring_with_examples_and_notes(self):
        doc = """
        Execute a sample command.

        [bold green]Examples:[/bold green]
          [cyan]$ stone sample[/cyan]                  # Standard run
          [cyan]$ stone sample --dry-run[/cyan]        # Dry run preview

        [bold yellow]Notes:[/bold yellow]
          Requires active network connection.
        """
        parsed = parse_docstring(doc)
        assert parsed["description"] == "Execute a sample command."
        assert len(parsed["examples"]) == 2
        assert parsed["examples"][0]["command"] == "stone sample"
        assert parsed["examples"][0]["description"] == "Standard run"
        assert parsed["examples"][1]["command"] == "stone sample --dry-run"
        assert parsed["examples"][1]["description"] == "Dry run preview"
        assert parsed["notes"] == "Requires active network connection."

    def test_dynamic_command_reflection(self):
        test_app = typer.Typer()

        @test_app.command("custom-task", short_help="Run custom user-defined task.")
        def custom_task(
            name: Annotated[str, typer.Argument(help="Target task name.")],
            force: Annotated[
                bool,
                typer.Option("--force", "-f", help="Force execution without prompt."),
            ] = False,
        ):
            """
            Execute a custom user-defined task with parameters.

            [bold green]Examples:[/bold green]
              [cyan]$ stone custom-task deploy[/cyan]          # Run deploy task
              [cyan]$ stone custom-task deploy --force[/cyan]  # Force deploy
            """

        clear_docs_cache()
        catalog = extract_cli_metadata(test_app, force_refresh=True)

        assert "custom-task" in catalog
        doc = catalog["custom-task"]
        assert doc["title"] == "custom-task - Run custom user-defined task."
        assert "Execute a custom user-defined task" in doc["description"]
        assert len(doc["arguments"]) == 1
        assert doc["arguments"][0]["name"] == "NAME"
        assert doc["arguments"][0]["required"] is True
        assert len(doc["options"]) == 1
        assert doc["options"][0]["flag"] == "--force / -f"
        assert len(doc["examples"]) == 2
        assert doc["examples"][0]["command"] == "stone custom-task deploy"

        md = generate_markdown_doc("custom-task", app=test_app)
        assert "custom-task" in md
        assert "--force / -f" in md
        assert "Run deploy task" in md


class TestMarkdownGenerator:
    def test_generate_markdown_unknown(self):
        md = generate_markdown_doc("nonexistent")
        assert "Topic Not Found" in md

    def test_all_topics_have_required_fields(self):
        catalog = extract_cli_metadata(app)
        for key, doc in catalog.items():
            assert "title" in doc
            assert "description" in doc
            if key != "overview":
                assert "usage" in doc
                assert "examples" in doc
