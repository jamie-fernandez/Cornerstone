"""Database management subcommands for SQLite, SQLAlchemy ORM, and Alembic migrations."""

from __future__ import annotations

import typer
from alembic import command
from rich.console import Console

from cli.commands.db.info import db_info_command, db_test_command
from cli.commands.db.migrations import (
    db_current_command,
    db_downgrade_command,
    db_history_command,
    db_migrate_command,
    db_revision_command,
    db_stamp_command,
    db_upgrade_command,
    get_next_revision_id,
)
from cli.commands.db.query import db_query_command
from cli.commands.db.schema import (
    db_init_command,
    db_reset_command,
    db_tables_command,
)

console = Console()

db_app = typer.Typer(
    name="db",
    help="""[bold cyan]Database Management[/bold cyan] - SQLite, SQLAlchemy ORM & Alembic migration commands.

[bold]Common Workflows:[/bold]
  [cyan]$ stone db info[/cyan]                                                # Check database file presence, size, and table names
  [cyan]$ stone db test[/cyan]                                                # Verify connection and execute a test query
  [cyan]$ stone db init[/cyan]                                                # Initialize database schema and apply migrations to head
  [cyan]$ stone db migrate -m "create_users_table"[/cyan]                     # Generate a new sequential migration revision
  [cyan]$ stone db upgrade[/cyan]                                             # Apply pending migrations to head
  [cyan]$ stone db downgrade[/cyan]                                           # Revert the latest migration
  [cyan]$ stone db current[/cyan]                                             # Show current database revision
  [cyan]$ stone db history[/cyan]                                             # View migration revision history
  [cyan]$ stone db tables[/cyan]                                              # Inspect column names, data types, and primary keys
  [cyan]$ stone db query "SELECT 1 AS status, 'active' AS state"[/cyan]       # Run an ad-hoc SQL query and view results in a table
  [cyan]$ stone db reset --yes[/cyan]                                         # Reset database without interactive confirmation prompt
""",
    rich_markup_mode="rich",
    no_args_is_help=True,
)

# Register info & inspection commands
db_app.command(
    "info", short_help="Show SQLite database status, location, size, and settings."
)(db_info_command)
db_app.command("test", short_help="Test database connection and query execution.")(
    db_test_command
)

# Register schema lifecycle & table inspection commands
db_app.command(
    "init",
    short_help="Initialize database and apply Alembic schema migrations to head.",
)(db_init_command)
db_app.command(
    "reset",
    short_help="Reset database by deleting existing file and re-running Alembic migrations.",
)(db_reset_command)
db_app.command("tables", short_help="List database tables and column schema details.")(
    db_tables_command
)

# Register query command
db_app.command("query", short_help="Execute an SQL query against the database.")(
    db_query_command
)

# Register migration commands
db_app.command(
    "migrate",
    short_help="Autogenerate or create a new Alembic database migration.",
)(db_migrate_command)
db_app.command("revision", hidden=True)(db_revision_command)
db_app.command(
    "upgrade",
    short_help="Upgrade database schema to a target Alembic revision.",
)(db_upgrade_command)
db_app.command(
    "downgrade",
    short_help="Revert database schema to a previous Alembic revision.",
)(db_downgrade_command)
db_app.command(
    "current",
    short_help="Display the current Alembic database migration revision.",
)(db_current_command)
db_app.command(
    "history",
    short_help="Display chronological Alembic migration revision history.",
)(db_history_command)
db_app.command(
    "stamp",
    short_help="Stamp database revision table without running SQL migrations.",
)(db_stamp_command)

__all__ = [
    "command",
    "db_app",
    "db_current_command",
    "db_downgrade_command",
    "db_history_command",
    "db_info_command",
    "db_init_command",
    "db_migrate_command",
    "db_query_command",
    "db_reset_command",
    "db_revision_command",
    "db_stamp_command",
    "db_tables_command",
    "db_test_command",
    "db_upgrade_command",
    "get_next_revision_id",
]
