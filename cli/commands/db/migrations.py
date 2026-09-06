"""Alembic database schema migrations subcommands."""

from __future__ import annotations

from typing import Annotated

import typer
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from rich.console import Console
from rich.table import Table

from app.database import (
    get_alembic_config,
    get_current_revision,
    get_db_path,
)

console = Console()


def get_next_revision_id(alembic_cfg: Config) -> str:
    """Determine the next sequential 4-digit revision ID (e.g. '0001', '0002')."""
    script_dir = ScriptDirectory.from_config(alembic_cfg)
    highest_int = 0
    for script in script_dir.walk_revisions():
        if script.revision and script.revision.isdigit():
            highest_int = max(highest_int, int(script.revision))
    return f"{highest_int + 1:04d}"


def db_migrate_command(
    message: Annotated[
        str | None,
        typer.Option(
            "--message",
            "-m",
            help="Migration description / message (e.g. 'create_users_table', 'add_email_to_users').",
        ),
    ] = None,
    autogenerate: Annotated[
        bool,
        typer.Option(
            "--autogenerate/--no-autogenerate",
            help="Autogenerate migration operations from SQLAlchemy ORM models.",
        ),
    ] = True,
    rev_id: Annotated[
        str | None,
        typer.Option(
            "--rev-id",
            "-r",
            help="Explicit revision ID (defaults to next sequential 4-digit number e.g. 0002).",
        ),
    ] = None,
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
    Generate a new Alembic migration revision script from SQLAlchemy models.

    [bold green]Examples:[/bold green]
      [cyan]$ stone db migrate -m "create_users_table"[/cyan]
      [cyan]$ stone db migrate -m "add_avatar_url_to_users"[/cyan]
      [cyan]$ stone db migrate -m "manual empty migration" --no-autogenerate[/cyan]
      [cyan]$ stone db migrate -p ./custom.db -m "schema update"[/cyan]
    """
    path = db_path or get_db_path()
    try:
        alembic_cfg = get_alembic_config(db_path=path)
        next_rev_id = rev_id or get_next_revision_id(alembic_cfg)
        script = command.revision(
            alembic_cfg,
            message=message,
            autogenerate=autogenerate,
            rev_id=next_rev_id,
        )
        if isinstance(script, list):
            script = script[0] if script else None

        rev_id_str = getattr(script, "revision", "unknown") if script else "unknown"
        path_str = getattr(script, "path", "") if script else ""
        console.print(
            f"[bold green]✓[/bold green] Created migration revision: [magenta]{rev_id_str}[/magenta]"
        )
        if path_str:
            console.print(f"File: [cyan]{path_str}[/cyan]")
    except Exception as e:  # noqa: BLE001 - top-level CLI guard
        console.print(f"[bold red]✗ Migration generation failed:[/bold red] {e}")
        raise typer.Exit(code=1)


def db_revision_command(
    message: Annotated[
        str | None,
        typer.Option("--message", "-m", help="Migration description / message."),
    ] = None,
    autogenerate: Annotated[
        bool,
        typer.Option(
            "--autogenerate/--no-autogenerate",
            help="Autogenerate migration operations from SQLAlchemy ORM models.",
        ),
    ] = True,
    rev_id: Annotated[
        str | None,
        typer.Option("--rev-id", "-r", help="Explicit revision ID."),
    ] = None,
    db_path: Annotated[
        str | None,
        typer.Option(
            "--db-path",
            "-p",
            help="Custom path to the SQLite database file.",
        ),
    ] = None,
):
    """Alias for 'db migrate'."""
    db_migrate_command(
        message=message,
        autogenerate=autogenerate,
        rev_id=rev_id,
        db_path=db_path,
    )


def db_upgrade_command(
    revision: Annotated[
        str,
        typer.Argument(
            help="Target Alembic revision identifier (e.g. 'head', '+1', or revision ID like '0002').",
        ),
    ] = "head",
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
    Apply database schema migrations forward up to the specified target revision.

    [bold green]Examples:[/bold green]
      [cyan]$ stone db upgrade[/cyan]             # Upgrade to head
      [cyan]$ stone db upgrade +1[/cyan]          # Upgrade one revision
      [cyan]$ stone db upgrade 0002[/cyan]        # Upgrade to specific revision
      [cyan]$ stone db upgrade -p ./app.db head[/cyan]
    """
    path = db_path or get_db_path()
    try:
        alembic_cfg = get_alembic_config(db_path=path)
        command.upgrade(alembic_cfg, revision)
        current_rev = get_current_revision(path)
        console.print(
            f"[bold green]✓[/bold green] Database upgraded to revision: [magenta]{current_rev or revision}[/magenta]"
        )
    except Exception as e:  # noqa: BLE001 - top-level CLI guard
        console.print(f"[bold red]✗ Database upgrade failed:[/bold red] {e}")
        raise typer.Exit(code=1)


def db_downgrade_command(
    revision: Annotated[
        str,
        typer.Argument(
            help="Target Alembic revision identifier (e.g. '-1', 'base', or revision ID like '0001').",
        ),
    ] = "-1",
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
    Revert database schema migrations backward to the specified target revision.

    [bold green]Examples:[/bold green]
      [cyan]$ stone db downgrade[/cyan]             # Revert 1 revision (-1)
      [cyan]$ stone db downgrade base[/cyan]        # Revert all migrations
      [cyan]$ stone db downgrade -p ./app.db -1[/cyan]
    """
    path = db_path or get_db_path()
    try:
        alembic_cfg = get_alembic_config(db_path=path)
        command.downgrade(alembic_cfg, revision)
        current_rev = get_current_revision(path)
        console.print(
            f"[bold green]✓[/bold green] Database downgraded to revision: [magenta]{current_rev or 'base'}[/magenta]"
        )
    except Exception as e:  # noqa: BLE001 - top-level CLI guard
        console.print(f"[bold red]✗ Database downgrade failed:[/bold red] {e}")
        raise typer.Exit(code=1)


def db_current_command(
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
        typer.Option("--json", "-j", help="Output current revision details as JSON."),
    ] = False,
):
    """
    Display current database migration revision, head revision, and status.

    [bold green]Examples:[/bold green]
      [cyan]$ stone db current[/cyan]
      [cyan]$ stone db current --json[/cyan]
      [cyan]$ stone db current -p ./data/app.db[/cyan]
    """
    path = db_path or get_db_path()
    try:
        current_rev = get_current_revision(path)
        alembic_cfg = get_alembic_config(db_path=path)
        script_dir = ScriptDirectory.from_config(alembic_cfg)
        head_rev = script_dir.get_current_head()

        data = {
            "path": path,
            "revision": current_rev,
            "head": head_rev,
            "is_head": bool(current_rev and current_rev == head_rev),
        }

        if as_json:
            console.print_json(data=data)
            return

        table = Table(
            title="[bold cyan]Database Migration State[/bold cyan]", show_header=True
        )
        table.add_column("Property", style="cyan", no_wrap=True)
        table.add_column("Value", style="magenta")

        table.add_row("Database Path", path)
        table.add_row("Current Revision", current_rev or "[dim]None (base)[/dim]")
        table.add_row("Head Revision", head_rev or "[dim]None[/dim]")
        table.add_row(
            "Status",
            (
                "[bold green]Up to date[/bold green]"
                if data["is_head"]
                else "[yellow]Pending migrations[/yellow]"
            ),
        )
        console.print(table)
    except Exception as e:  # noqa: BLE001 - top-level CLI guard
        if as_json:
            console.print_json(
                data={"status": "error", "message": str(e), "path": path}
            )
        else:
            console.print(
                f"[bold red]✗ Failed to inspect current revision:[/bold red] {e}"
            )
        raise typer.Exit(code=1)


def db_history_command(
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Show detailed revision history."),
    ] = False,
    as_json: Annotated[
        bool,
        typer.Option("--json", "-j", help="Output migration history as JSON."),
    ] = False,
):
    """
    Display chronological migration revision history and descriptions.

    [bold green]Examples:[/bold green]
      [cyan]$ stone db history[/cyan]
      [cyan]$ stone db history --verbose[/cyan]
      [cyan]$ stone db history --json[/cyan]
    """
    try:
        alembic_cfg = get_alembic_config()
        script_dir = ScriptDirectory.from_config(alembic_cfg)
        revisions = list(script_dir.walk_revisions())
        revisions.reverse()  # Chronological order from oldest to newest

        history_data = [
            {
                "revision": rev.revision,
                "down_revision": rev.down_revision,
                "message": (rev.doc or "").strip(),
                "branch_labels": (
                    list(rev.branch_labels)
                    if getattr(rev, "branch_labels", None)
                    else []
                ),
                "dependencies": (
                    list(rev.dependencies) if getattr(rev, "dependencies", None) else []
                ),
            }
            for rev in revisions
        ]

        if as_json:
            console.print_json(data=history_data)
            return

        if not revisions:
            console.print("[yellow]No migration revisions found.[/yellow]")
            return

        table = Table(
            title="[bold cyan]Migration Revision History[/bold cyan]", show_header=True
        )
        table.add_column("Revision", style="cyan", no_wrap=True)
        table.add_column("Down Revision", style="yellow")
        table.add_column("Description", style="green")
        if verbose:
            table.add_column("Branch Labels", style="magenta")
            table.add_column("Dependencies", style="blue")

        for item in history_data:
            row = [
                item["revision"],
                str(item["down_revision"]) if item["down_revision"] else "<base>",
                item["message"] or "[dim]No description[/dim]",
            ]
            if verbose:
                row.append(str(item["branch_labels"]) if item["branch_labels"] else "")
                row.append(str(item["dependencies"]) if item["dependencies"] else "")
            table.add_row(*row)

        console.print(table)
    except Exception as e:  # noqa: BLE001 - top-level CLI guard
        if as_json:
            console.print_json(data={"status": "error", "message": str(e)})
        else:
            console.print(
                f"[bold red]✗ Failed to read migration history:[/bold red] {e}"
            )
        raise typer.Exit(code=1)


def db_stamp_command(
    revision: Annotated[
        str,
        typer.Argument(
            help="Target Alembic revision to stamp (e.g. 'head', 'base', or revision ID).",
        ),
    ] = "head",
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
    Stamp the Alembic database revision table with a specific revision without executing migrations.

    [bold green]Examples:[/bold green]
      [cyan]$ stone db stamp head[/cyan]
      [cyan]$ stone db stamp base[/cyan]
      [cyan]$ stone db stamp 0001[/cyan]
      [cyan]$ stone db stamp -p ./custom.db head[/cyan]
    """
    path = db_path or get_db_path()
    try:
        alembic_cfg = get_alembic_config(db_path=path)
        command.stamp(alembic_cfg, revision)
        console.print(
            f"[bold green]✓[/bold green] Stamped database at [cyan]{path}[/cyan] with revision: [magenta]{revision}[/magenta]"
        )
    except Exception as e:  # noqa: BLE001 - top-level CLI guard
        console.print(f"[bold red]✗ Failed to stamp database revision:[/bold red] {e}")
        raise typer.Exit(code=1)
