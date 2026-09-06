"""Database status, inspection, and connection test commands."""

from __future__ import annotations

import os
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table
from sqlalchemy import inspect, text

from app.database import get_db_path, get_session, init_db

console = Console()


def db_info_command(
    db_path: Annotated[
        str | None,
        typer.Option(
            "--db-path",
            "-p",
            help="Custom path to the SQLite database file.",
        ),
    ] = None,
    as_json: Annotated[
        bool,
        typer.Option("--json", "-j", help="Output database info as JSON."),
    ] = False,
):
    """
    Show SQLite database status, location, size, PRAGMA settings, and tables.

    [bold green]Examples:[/bold green]
      [cyan]$ stone db info[/cyan]
      [cyan]$ stone db info --db-path ./data/app.db[/cyan]
      [cyan]$ stone db info --json[/cyan]
    """
    path = db_path or get_db_path()
    exists = os.path.isfile(path)
    size_bytes = os.path.getsize(path) if exists else 0

    tables = []
    journal_mode = None
    foreign_keys = None

    if exists:
        try:
            engine, _ = init_db(path)
            with engine.connect() as conn:
                journal_mode = conn.execute(text("PRAGMA journal_mode")).scalar()
                foreign_keys = conn.execute(text("PRAGMA foreign_keys")).scalar()
                inspector = inspect(conn)
                tables = inspector.get_table_names()
        except Exception as e:  # noqa: BLE001 - catch runtime inspection error and report
            tables = [f"Error inspecting DB: {e}"]

    data = {
        "path": path,
        "exists": exists,
        "size_bytes": size_bytes,
        "size_formatted": (
            f"{size_bytes / 1024:.2f} KB"
            if size_bytes < 1024 * 1024
            else f"{size_bytes / (1024 * 1024):.2f} MB"
        ),
        "journal_mode": str(journal_mode) if journal_mode else "N/A",
        "foreign_keys": bool(foreign_keys) if foreign_keys is not None else False,
        "tables": tables,
    }

    if as_json:
        console.print_json(data=data)
        return

    table = Table(title="[bold cyan]Database Information[/bold cyan]", show_header=True)
    table.add_column("Property", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")

    table.add_row("Database Path", data["path"])
    table.add_row(
        "File Exists",
        "[green]Yes[/green]" if data["exists"] else "[red]No[/red]",
    )
    table.add_row("File Size", data["size_formatted"] if data["exists"] else "0 KB")
    table.add_row("Journal Mode", data["journal_mode"])
    table.add_row(
        "Foreign Keys",
        "[green]ON[/green]" if data["foreign_keys"] else "[red]OFF[/red]",
    )
    table.add_row(
        "Tables",
        ", ".join(tables) if tables else "[dim]None[/dim]",
    )

    console.print(table)


def db_test_command(
    db_path: Annotated[
        str | None,
        typer.Option(
            "--db-path",
            "-p",
            help="Custom path to the SQLite database file.",
        ),
    ] = None,
    as_json: Annotated[
        bool,
        typer.Option("--json", "-j", help="Output result as JSON."),
    ] = False,
):
    """
    Test database connection and verify query execution.

    [bold green]Examples:[/bold green]
      [cyan]$ stone db test[/cyan]
      [cyan]$ stone db test --db-path ./custom.db[/cyan]
      [cyan]$ stone db test --json[/cyan]
    """
    path = db_path or get_db_path()
    try:
        init_db(path)
        with get_session() as session:
            result = session.execute(text("SELECT 1")).scalar()
            if result == 1:
                if as_json:
                    console.print_json(
                        data={
                            "status": "success",
                            "message": "Database connection OK",
                            "path": path,
                        }
                    )
                else:
                    console.print(
                        f"[bold green]✓[/bold green] Database connection OK at [cyan]{path}[/cyan]"
                    )
                return
            else:
                raise RuntimeError(f"Unexpected query result: {result}")
    except Exception as e:  # noqa: BLE001 - top-level CLI guard: report DB test failure
        if as_json:
            console.print_json(
                data={"status": "error", "message": str(e), "path": path}
            )
        else:
            console.print(f"[bold red]✗ Database connection failed:[/bold red] {e}")
        raise typer.Exit(code=1)
