"""Main Typer CLI application for Cornerstone."""

from __future__ import annotations

import platform
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from app.config import CONFIG
from app.database import get_db_path
from cli.commands.db import db_app
from cli.commands.docs import docs_command

app = typer.Typer(
    name=CONFIG.get("SLUG", "cornerstone"),
    help="""[bold cyan]Cornerstone CLI[/bold cyan] - Cross-platform desktop application CLI.

[bold]Common Workflows:[/bold]
  [cyan]$ uv run stone setup[/cyan]              # Install Bun/UV and dependencies (or python3 -m cli setup)
  [cyan]$ uv run stone dev[/cyan]                # Start development environment
  [cyan]$ uv run stone db info[/cyan]            # Inspect SQLite database status
  [cyan]$ uv run stone build[/cyan]              # Build desktop executable
  [cyan]$ uv run stone clean[/cyan]              # Clean build artifacts and temporary files
  [cyan]$ uv run stone docs[/cyan]               # Browse CLI interactive documentation

[bold]Direct CLI Invocations:[/bold]
  • With UV:           [cyan]$ uv run stone <command>[/cyan]
  • Active venv:       [cyan]$ stone <command>[/cyan]
  • Global tool:       [cyan]$ uv tool install --editable .[/cyan] -> [cyan]$ stone <command>[/cyan]
""",
    rich_markup_mode="rich",
    no_args_is_help=True,
)
app.add_typer(db_app, name="db")
app.command(
    "docs",
    short_help="Browse comprehensive CLI documentation, commands catalog, and usage examples.",
)(docs_command)

console = Console()


@app.command("version", short_help="Print application and CLI version.")
def version_command(
    as_json: Annotated[
        bool,
        typer.Option("--json", "-j", help="Output version information as JSON."),
    ] = False,
):
    """
    Print application name, slug, version, and Python runtime version.

    [bold green]Examples:[/bold green]
      [cyan]$ python3 -m cli version[/cyan]                  # Display human-readable formatted version string
      [cyan]$ python3 -m cli version --json[/cyan]           # Output version details as JSON for CI/CD scripting
    """
    data = {
        "name": CONFIG.get("NAME"),
        "slug": CONFIG.get("SLUG"),
        "version": CONFIG.get("VERSION"),
        "python": platform.python_version(),
    }
    if as_json:
        console.print_json(data=data)
    else:
        console.print(
            f"[bold green]{data['name']}[/bold green] version "
            f"[bold cyan]{data['version']}[/bold cyan] (Python {data['python']})"
        )


@app.command(
    "info", short_help="Display application details and runtime configuration."
)
def info_command(
    as_json: Annotated[
        bool,
        typer.Option("--json", "-j", help="Output configuration as JSON format."),
    ] = False,
):
    """
    Display application details and runtime configuration (paths, debug flag, database location).

    [bold green]Examples:[/bold green]
      [cyan]$ python3 -m cli info[/cyan]                     # Print formatted table of runtime paths, debug flag, and DB path
      [cyan]$ python3 -m cli info --json[/cyan]              # Export runtime configuration as JSON
      [cyan]$ python3 -m cli info -j[/cyan]                  # Export runtime configuration as JSON (short flag)
    """
    from app.api import API

    api = API()
    app_config_res = api.get_app_configuration()
    app_config = (
        app_config_res.get("data", app_config_res)
        if isinstance(app_config_res, dict)
        else CONFIG
    )
    db_path = get_db_path()

    info_data = {
        "name": app_config.get("NAME"),
        "slug": app_config.get("SLUG"),
        "version": app_config.get("VERSION"),
        "debug": app_config.get("DEBUG"),
        "base_path": app_config.get("BASE_PATH"),
        "html_path": app_config.get("HTML_PATH"),
        "db_path": db_path,
        "python_version": platform.python_version(),
    }
    if as_json:
        console.print_json(data=info_data)
        return

    table = Table(
        title="[bold green]Application Configuration[/bold green]", show_header=True
    )
    table.add_column("Key", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")

    for k, v in info_data.items():
        table.add_row(str(k), str(v))

    console.print(table)


@app.command("stats", short_help="Show system resource usage and hardware statistics.")
def stats_command(
    as_json: Annotated[
        bool,
        typer.Option("--json", "-j", help="Output system stats as JSON."),
    ] = False,
):
    """
    Show system resource usage and hardware statistics (CPU, memory, disk, and OS info).

    [bold green]Examples:[/bold green]
      [cyan]$ python3 -m cli stats[/cyan]                    # Display table with live CPU, memory, and disk utilization metrics
      [cyan]$ python3 -m cli stats --json[/cyan]             # Get structured metrics payload
    """
    from app.api import API

    api = API()
    stats_res = api.get_system_stats()
    stats = (
        stats_res.get("data", stats_res) if isinstance(stats_res, dict) else stats_res
    )

    sys_info_res = api.get_system_info()
    sys_info = (
        sys_info_res.get("data", sys_info_res)
        if isinstance(sys_info_res, dict)
        else sys_info_res
    )

    combined = {
        "system": sys_info,
        "stats": stats,
    }

    if as_json:
        console.print_json(data=combined)
        return

    table = Table(
        title="[bold blue]System Information & Stats[/bold blue]", show_header=True
    )
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Platform", f"{sys_info.get('platform')} ({sys_info.get('machine')})")
    table.add_row("OS Version", str(sys_info.get("version")))
    table.add_row("Python", str(sys_info.get("python_version")))
    table.add_row("CPU Usage", f"{stats.get('cpu_percent')}%")

    mem = stats.get("memory", {})
    mem_total_gb = mem.get("total", 0) / (1024**3)
    mem_avail_gb = mem.get("available", 0) / (1024**3)
    table.add_row(
        "Memory",
        f"{mem.get('percent_used')}% used ({mem_avail_gb:.2f} GB avail / {mem_total_gb:.2f} GB total)",
    )

    disk = stats.get("disk", {})
    disk_total_gb = disk.get("total", 0) / (1024**3)
    disk_used_gb = disk.get("used", 0) / (1024**3)
    table.add_row(
        "Disk",
        f"{disk.get('percent_used')}% used ({disk_used_gb:.2f} GB used / {disk_total_gb:.2f} GB total)",
    )

    console.print(table)


@app.command("users", short_help="List example user data from API.")
def users_command(
    as_json: Annotated[
        bool,
        typer.Option("--json", "-j", help="Output user data as JSON."),
    ] = False,
):
    """
    List example user records retrieved via the Python backend API.

    [bold green]Examples:[/bold green]
      [cyan]$ python3 -m cli users[/cyan]                    # Display formatted table of sample users
      [cyan]$ python3 -m cli users --json[/cyan]             # Export user records as JSON array
    """
    from app.api import API

    api = API()
    res = api.get_user_data()
    data = res.get("data", res) if isinstance(res, dict) else res
    users = data.get("users", []) if isinstance(data, dict) else []

    if as_json:
        console.print_json(data=users)
        return

    table = Table(title="[bold yellow]User Data[/bold yellow]", show_header=True)
    table.add_column("ID", style="cyan", justify="right")
    table.add_column("Name", style="green")
    table.add_column("Email", style="blue")

    for user in users:
        table.add_row(
            str(user.get("id")), str(user.get("name")), str(user.get("email"))
        )

    console.print(table)


@app.command(
    "dev",
    short_help="Start development environment (Vite frontend + pywebview backend).",
)
def dev_command():
    """
    Start development environment with hot reloading (Vite frontend + pywebview backend).

    [bold green]Examples:[/bold green]
      [cyan]$ python3 -m cli dev[/cyan]                      # Start the Vite dev server and launch the desktop window
      [cyan]$ just dev[/cyan]                                # Shortcut alias via just command runner

    [bold yellow]Notes:[/bold yellow]
      Ensure dependencies are installed first (`python3 -m cli setup`). Press Ctrl+C in the terminal to gracefully stop both servers.
    """
    from cli.commands.dev import main as dev_main

    try:
        dev_main()
    except KeyboardInterrupt:
        pass


@app.command(
    "build",
    short_help="Build production frontend assets and PyInstaller executable.",
)
def build_command():
    """
    Build production frontend assets (Vite) and package standalone PyInstaller executable.

    [bold green]Examples:[/bold green]
      [cyan]$ python3 -m cli build[/cyan]                    # Build frontend assets into dist/ and generate the standalone desktop executable
      [cyan]$ just build[/cyan]                              # Shortcut alias via just command runner

    [bold yellow]Notes:[/bold yellow]
      Outputs are written to the 'dist/' directory. Requires PyInstaller and Bun to be available.
    """
    from cli.commands.build import main as build_main

    build_main()


@app.command(
    "clean",
    short_help="Clean up folders and files built by the build command.",
)
def clean_command(
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run",
            "-n",
            help="Show what files and directories would be removed without deleting them.",
        ),
    ] = False,
    as_json: Annotated[
        bool,
        typer.Option(
            "--json",
            "-j",
            help="Output result as JSON.",
        ),
    ] = False,
):
    """
    Clean up build artifacts produced by Vite and PyInstaller (dist/, build/, ui/dist/, *.spec).

    [bold green]Examples:[/bold green]
      [cyan]$ python3 -m cli clean[/cyan]                    # Remove all build artifacts and temporary files
      [cyan]$ python3 -m cli clean --dry-run[/cyan]          # Preview build artifacts to delete without removing them
      [cyan]$ python3 -m cli clean --json[/cyan]             # Output clean results as structured JSON
      [cyan]$ just clean[/cyan]                              # Shortcut alias via just command runner

    [bold yellow]Notes:[/bold yellow]
      Deletes 'dist/', 'build/', 'ui/dist/', and PyInstaller '.spec' files from the project root.
    """
    from cli.commands.clean import clean_artifacts

    clean_artifacts(dry_run=dry_run, as_json=as_json)


@app.command(
    "setup",
    short_help="Initialize development environment (install Bun, UV, dependencies).",
)
def setup_command():
    """
    Initialize development environment by verifying/installing Bun, UV, and all dependencies.

    [bold green]Examples:[/bold green]
      [cyan]$ python3 -m cli setup[/cyan]                    # Check for Bun and UV, install if missing, and sync all packages
      [cyan]$ just setup[/cyan]                              # Shortcut alias via just command runner

    [bold yellow]Notes:[/bold yellow]
      Idempotent: safe to re-run whenever package.json or pyproject.toml changes.
    """
    from cli.commands.setup import setup as setup_main

    setup_main()


@app.command("init", short_help="Rebrand this template into your own application.")
def init_command(
    name: Annotated[
        list[str],
        typer.Argument(help='Human-facing app name, e.g. "My App"'),
    ],
    description: Annotated[
        str,
        typer.Option("--description", "-d", help="Short project description"),
    ] = "",
    alias: Annotated[
        list[str] | None,
        typer.Option(
            "--alias",
            "-a",
            help="Custom CLI command alias(es) (e.g. -a stone)",
        ),
    ] = None,
    clean_examples: Annotated[
        bool,
        typer.Option(
            "--clean-examples",
            help="Remove placeholder example code",
        ),
    ] = False,
):
    """
    Rebrand this template into your own customized desktop application.

    [bold green]Examples:[/bold green]
      [cyan]$ python3 -m cli init "My Awesome App"[/cyan]                               # Rebrand template with a new application name
      [cyan]$ python3 -m cli init "Task Flow" -d "A lightweight desktop task manager" --alias tf -a stone[/cyan] # Rebrand with a custom description, CLI aliases, and script registration
      [cyan]$ python3 -m cli init "Note Forge" -a nf --clean-examples[/cyan]               # Rebrand with an alias and purge example/demo code

    [bold yellow]Notes:[/bold yellow]
      Updates pyproject.toml ([project.scripts] and metadata), package.json, README.md, and AGENTS.md automatically.
    """
    from cli.commands.init import rebrand

    display_name = " ".join(name).strip()
    if not display_name:
        console.print("[bold red]Error:[/bold red] app name must not be empty")
        raise typer.Exit(code=2)
    rebrand(display_name, description, clean_examples, aliases=alias)


if __name__ == "__main__":
    app()
