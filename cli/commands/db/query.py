"""Database ad-hoc SQL query execution command."""

from __future__ import annotations

from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table
from sqlalchemy import text

from app.database import get_db_path, get_session, init_db

console = Console()


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
