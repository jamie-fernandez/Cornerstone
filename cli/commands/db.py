"""Database management subcommands for SQLite / SQLAlchemy."""

from __future__ import annotations

import os
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table
from sqlalchemy import inspect, text

from app.database import get_db_path, get_session, init_db, shutdown_db

db_app = typer.Typer(
    name="db",
    help="""[bold cyan]Database Management[/bold cyan] - SQLite & SQLAlchemy commands.

[bold]Common Workflows:[/bold]
  [cyan]$ python3 -m cli db info[/cyan]                                                # Check database file presence, size, and table names
  [cyan]$ python3 -m cli db test[/cyan]                                                # Verify connection and execute a test query
  [cyan]$ python3 -m cli db init[/cyan]                                                # Initialize database schema
  [cyan]$ python3 -m cli db tables[/cyan]                                              # Inspect column names, data types, and primary keys
  [cyan]$ python3 -m cli db query "SELECT 1 AS status, 'active' AS state"[/cyan]       # Run an ad-hoc SQL query and view results in a table
  [cyan]$ python3 -m cli db reset --yes[/cyan]                                          # Reset database without interactive confirmation prompt
""",
    rich_markup_mode="rich",
    no_args_is_help=True,
)

console = Console()


@db_app.command(
    "info", short_help="Show SQLite database status, location, size, and settings."
)
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
      [cyan]$ python3 -m cli db info[/cyan]
      [cyan]$ python3 -m cli db info --db-path ./data/app.db[/cyan]
      [cyan]$ python3 -m cli db info --json[/cyan]
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


@db_app.command("test", short_help="Test database connection and query execution.")
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
      [cyan]$ python3 -m cli db test[/cyan]
      [cyan]$ python3 -m cli db test --db-path ./custom.db[/cyan]
      [cyan]$ python3 -m cli db test --json[/cyan]
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


@db_app.command("init", short_help="Initialize database and create all schema tables.")
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
        tables = inspector.get_table_names()
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


@db_app.command(
    "reset",
    short_help="Reset database by deleting existing file and recreating schema.",
)
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
      [cyan]$ python3 -m cli db reset[/cyan]                # Prompts for confirmation
      [cyan]$ python3 -m cli db reset --yes[/cyan]          # Skip interactive confirmation
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


@db_app.command("tables", short_help="List database tables and column schema details.")
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
    table_names = inspector.get_table_names()

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


@db_app.command("query", short_help="Execute an SQL query against the database.")
def db_query_command(
    sql: Annotated[
        str,
        typer.Argument(help="SQL statement to execute (e.g. 'SELECT 1 AS num')"),
    ],
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
        typer.Option("--json", "-j", help="Output query results as JSON."),
    ] = False,
):
    """
    Execute an arbitrary SQL query against the SQLite database and display results.

    [bold green]Examples:[/bold green]
      [cyan]$ python3 -m cli db query "SELECT 1 AS status, 'ok' AS message"[/cyan]
      [cyan]$ python3 -m cli db query "SELECT * FROM users"[/cyan]
      [cyan]$ python3 -m cli db query "SELECT count(*) FROM users" --json[/cyan]
    """
    path = db_path or get_db_path()
    init_db(path)
    try:
        with get_session() as session:
            result = session.execute(text(sql))
            if result.returns_rows:
                keys = list(result.keys())
                rows = [list(r) for r in result.fetchall()]

                if as_json:
                    dict_rows = [dict(zip(keys, row, strict=False)) for row in rows]
                    console.print_json(data=dict_rows)
                    return

                table = Table(
                    title=f"[bold green]SQL Query Results: {sql}[/bold green]",
                    show_header=True,
                )
                for key in keys:
                    table.add_column(str(key), style="cyan")
                for row in rows:
                    table.add_row(*[str(val) for val in row])
                console.print(table)
                console.print(f"[dim]{len(rows)} row(s) returned[/dim]")
            else:
                rowcount = result.rowcount
                if as_json:
                    console.print_json(data={"status": "success", "rowcount": rowcount})
                else:
                    console.print(
                        f"[bold green]Query executed successfully.[/bold green] Rows affected: [cyan]{rowcount}[/cyan]"
                    )
    except Exception as e:  # noqa: BLE001 - top-level CLI guard: report query failure
        if as_json:
            console.print_json(data={"status": "error", "message": str(e)})
        else:
            console.print(f"[bold red]✗ SQL execution failed:[/bold red] {e}")
        raise typer.Exit(code=1)
