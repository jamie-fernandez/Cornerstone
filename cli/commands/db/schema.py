"""Database initialization, reset, and table schema inspection commands."""

from __future__ import annotations

import os
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table
from sqlalchemy import inspect

from app.database import get_db_path, init_db, shutdown_db

console = Console()


def db_init_command(
    db_path: Annotated[
        str | None,
        typer.Option(
            "--db-path",
            "-p",
            help="Custom path to the SQLite database file.",
        ),
    ] = None,
):
    """
    Initialize SQLite database file and create all defined schema tables.

    [bold green]Examples:[/bold green]
      [cyan]$ python3 -m cli db init[/cyan]
      [cyan]$ python3 -m cli db init -p ./data/app.db[/cyan]
    """
    path = db_path or get_db_path()
    try:
        engine, _ = init_db(path)
        inspector = inspect(engine)
        tables = [t for t in inspector.get_table_names() if t != "alembic_version"]
        console.print(
            f"[bold green]✓[/bold green] Database initialized at: [cyan]{path}[/cyan]"
        )
        if tables:
            console.print(
                f"Created/verified tables: [magenta]{', '.join(tables)}[/magenta]"
            )
        else:
            console.print(
                "[yellow]Schema ready. No custom model tables defined yet.[/yellow]"
            )
    except Exception as e:  # noqa: BLE001 - top-level CLI guard: report DB init failure
        console.print(f"[bold red]✗ Database initialization failed:[/bold red] {e}")
        raise typer.Exit(code=1)


def db_reset_command(
    yes: Annotated[
        bool,
        typer.Option(
            "--yes",
            "-y",
            help="Confirm database reset without interactive prompt.",
        ),
    ] = False,
    db_path: Annotated[
        str | None,
        typer.Option(
            "--db-path",
            "-p",
            help="Custom path to the SQLite database file.",
        ),
    ] = None,
):
    """
    Reset database by deleting existing database file and recreating schema.

    [bold green]Examples:[/bold green]
      [cyan]$ python3 -m cli db reset[/cyan]                 # Prompts for confirmation
      [cyan]$ python3 -m cli db reset --yes[/cyan]           # Skip interactive confirmation
      [cyan]$ python3 -m cli db reset -p ./test.db -y[/cyan] # Reset custom DB path
    """
    path = db_path or get_db_path()
    if not yes:
        confirm = typer.confirm(
            f"Are you sure you want to reset the database at '{path}'? All data will be lost."
        )
        if not confirm:
            console.print("[yellow]Operation cancelled.[/yellow]")
            raise typer.Abort()

    shutdown_db()
    if os.path.exists(path):
        try:
            os.remove(path)
            console.print(
                f"[bold yellow]Removed database file:[/bold yellow] [cyan]{path}[/cyan]"
            )
        except OSError as e:
            console.print(f"[bold red]✗ Failed to delete database file:[/bold red] {e}")
            raise typer.Exit(code=1)

    init_db(path)
    console.print(
        f"[bold green]✓[/bold green] Database recreated and initialized at: [cyan]{path}[/cyan]"
    )


def db_tables_command(
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
        typer.Option("--json", "-j", help="Output table schema as JSON."),
    ] = False,
):
    """
    List all database tables and inspect column schema details (types, nullable, PKs).

    [bold green]Examples:[/bold green]
      [cyan]$ python3 -m cli db tables[/cyan]
      [cyan]$ python3 -m cli db tables --json[/cyan]
      [cyan]$ python3 -m cli db tables -p ./custom.db[/cyan]
    """
    path = db_path or get_db_path()
    engine, _ = init_db(path)
    inspector = inspect(engine)
    table_names = [t for t in inspector.get_table_names() if t != "alembic_version"]

    tables_data = {}
    for table_name in table_names:
        cols = inspector.get_columns(table_name)
        pk_constraint = inspector.get_pk_constraint(table_name)
        pk_cols = pk_constraint.get("constrained_columns", []) if pk_constraint else []
        tables_data[table_name] = [
            {
                "name": col["name"],
                "type": str(col["type"]),
                "nullable": col.get("nullable", True),
                "primary_key": col["name"] in pk_cols,
                "default": (
                    str(col.get("default", ""))
                    if col.get("default") is not None
                    else None
                ),
            }
            for col in cols
        ]

    if as_json:
        console.print_json(data=tables_data)
        return

    if not table_names:
        console.print("[yellow]No tables found in the database.[/yellow]")
        return

    for table_name, cols in tables_data.items():
        table = Table(
            title=f"[bold cyan]Table: {table_name}[/bold cyan]", show_header=True
        )
        table.add_column("Column", style="green", no_wrap=True)
        table.add_column("Type", style="magenta")
        table.add_column("Nullable", style="yellow")
        table.add_column("Primary Key", style="red")

        for col in cols:
            table.add_row(
                col["name"],
                col["type"],
                "YES" if col["nullable"] else "NO",
                "✓" if col["primary_key"] else "",
            )
        console.print(table)
