"""System environment and dependency diagnostics."""

from __future__ import annotations

import os
import platform
import shutil
import sqlite3
import subprocess
import sys
from typing import Annotated, Any, TypedDict

import typer
from rich.console import Console
from rich.table import Table

from cli.common import BUN_DEFAULT, PROJECT_ROOT, UV_DEFAULT, find_executable

console = Console()


class DiagnosticCheck(TypedDict):
    name: str
    category: str
    status: str  # "ok", "warning", "error"
    value: str
    details: str
    remediation: str | None


def check_python_version() -> DiagnosticCheck:
    """Check Python runtime version (>= 3.13 required)."""
    version_str = platform.python_version()
    major, minor, _micro = sys.version_info[:3]
    if (major, minor) >= (3, 13):
        return {
            "name": "Python Runtime",
            "category": "runtime",
            "status": "ok",
            "value": f"v{version_str}",
            "details": f"Python {version_str} meets requirement (>= 3.13)",
            "remediation": None,
        }
    return {
        "name": "Python Runtime",
        "category": "runtime",
        "status": "error",
        "value": f"v{version_str}",
        "details": f"Python {version_str} is below required version 3.13+",
        "remediation": "Install Python 3.13 or newer via uv (uv python install 3.14) or your system package manager.",
    }


def check_uv() -> DiagnosticCheck:
    """Check UV package manager availability and version."""
    uv_path = find_executable("uv", UV_DEFAULT)
    if shutil.which("uv") or os.path.isfile(uv_path):
        try:
            res = subprocess.run(
                [uv_path, "--version"],
                capture_output=True,
                text=True,
                check=True,
                timeout=5,
            )
            version = res.stdout.strip()
            return {
                "name": "UV Package Manager",
                "category": "package_manager",
                "status": "ok",
                "value": version,
                "details": f"Located at {uv_path}",
                "remediation": None,
            }
        except Exception as e:  # noqa: BLE001
            return {
                "name": "UV Package Manager",
                "category": "package_manager",
                "status": "warning",
                "value": "Error checking version",
                "details": f"Executable found but failed to run: {e}",
                "remediation": "Reinstall UV: curl -LsSf https://astral.sh/uv/install.sh | sh",
            }
    return {
        "name": "UV Package Manager",
        "category": "package_manager",
        "status": "error",
        "value": "Not found",
        "details": "UV is required for managing Python dependencies.",
        "remediation": "Install UV via 'curl -LsSf https://astral.sh/uv/install.sh | sh' or run 'stone setup'.",
    }


def check_bun() -> DiagnosticCheck:
    """Check Bun runtime and package manager availability."""
    bun_path = find_executable("bun", BUN_DEFAULT)
    if shutil.which("bun") or os.path.isfile(bun_path):
        try:
            res = subprocess.run(
                [bun_path, "--version"],
                capture_output=True,
                text=True,
                check=True,
                timeout=5,
            )
            version = res.stdout.strip()
            return {
                "name": "Bun Runtime",
                "category": "package_manager",
                "status": "ok",
                "value": f"v{version}",
                "details": f"Located at {bun_path}",
                "remediation": None,
            }
        except Exception as e:  # noqa: BLE001
            return {
                "name": "Bun Runtime",
                "category": "package_manager",
                "status": "warning",
                "value": "Error checking version",
                "details": f"Executable found but failed to run: {e}",
                "remediation": "Reinstall Bun: curl -fsSL https://bun.sh/install | bash",
            }
    return {
        "name": "Bun Runtime",
        "category": "package_manager",
        "status": "error",
        "value": "Not found",
        "details": "Bun is required for managing frontend dependencies and building UI assets.",
        "remediation": "Install Bun via 'curl -fsSL https://bun.sh/install | bash' or run 'stone setup'.",
    }


def check_gui_engine() -> DiagnosticCheck:
    """Check OS-specific GUI engine prerequisites for pywebview."""
    current_os = sys.platform
    if current_os == "darwin":
        # macOS uses Cocoa WebKit (built-in)
        return {
            "name": "Desktop GUI Engine",
            "category": "gui",
            "status": "ok",
            "value": "macOS WebKit (Cocoa)",
            "details": "Native macOS WebKit framework available.",
            "remediation": None,
        }
    if current_os == "win32":
        # Windows uses WebView2 or MSHTML
        return {
            "name": "Desktop GUI Engine",
            "category": "gui",
            "status": "ok",
            "value": "Windows WebView2",
            "details": "Windows Edge WebView2 runtime supported.",
            "remediation": "If webview window fails to open, install Microsoft Edge WebView2 Evergreen Runtime.",
        }
    if current_os.startswith("linux"):
        # Linux requires GTK3 and WebKit2GTK, plus DISPLAY or WAYLAND_DISPLAY
        display = os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")
        has_display = bool(display)

        # Check for webkit2gtk
        has_webkit = False
        try:
            import gi  # type: ignore

            gi.require_version("WebKit2", "4.1")
            from gi.repository import WebKit2  # type: ignore

            has_webkit = True
        except Exception:  # noqa: BLE001
            try:
                import gi  # type: ignore

                gi.require_version("WebKit2", "4.0")
                from gi.repository import WebKit2  # type: ignore # noqa: F401

                has_webkit = True
            except Exception:  # noqa: BLE001
                has_webkit = False

        if has_webkit and has_display:
            return {
                "name": "Desktop GUI Engine",
                "category": "gui",
                "status": "ok",
                "value": "Linux WebKit2GTK",
                "details": f"WebKit2GTK loaded successfully (display: {display})",
                "remediation": None,
            }
        elif not has_display:
            return {
                "name": "Desktop GUI Engine",
                "category": "gui",
                "status": "warning",
                "value": "No graphical display detected",
                "details": "Neither DISPLAY nor WAYLAND_DISPLAY environment variable is set (headless/CI environment).",
                "remediation": "For desktop GUI execution, run within an active X11 or Wayland session, or use Xvfb (e.g. xvfb-run stone dev).",
            }
        else:
            return {
                "name": "Desktop GUI Engine",
                "category": "gui",
                "status": "error",
                "value": "WebKit2GTK missing",
                "details": "Python GObject bindings (WebKit2) not found.",
                "remediation": "Install WebKit2GTK: 'sudo apt-get install -y python3-gi gir1.2-webkit2-4.1' (Ubuntu/Debian) or 'sudo dnf install webkit2gtk4.1-devel' (Fedora).",
            }

    return {
        "name": "Desktop GUI Engine",
        "category": "gui",
        "status": "warning",
        "value": current_os,
        "details": f"Untested platform: {current_os}",
        "remediation": None,
    }


def check_database() -> DiagnosticCheck:
    """Check SQLite availability and project database write permissions."""
    try:
        # Check sqlite3 version
        sqlite_version = sqlite3.sqlite_version

        # Check database directory writeability
        from app.database import get_db_path, get_session

        db_path = get_db_path()
        db_dir = os.path.dirname(os.path.abspath(db_path))
        os.makedirs(db_dir, exist_ok=True)

        if not os.access(db_dir, os.W_OK):
            return {
                "name": "SQLite Database & Storage",
                "category": "database",
                "status": "error",
                "value": f"SQLite v{sqlite_version}",
                "details": f"Database directory '{db_dir}' is not writable.",
                "remediation": f"Adjust file permissions on '{db_dir}' to allow write access.",
            }

        # Verify query execution
        with get_session() as session:
            from sqlalchemy import text

            session.execute(text("SELECT 1"))

        return {
            "name": "SQLite Database & Storage",
            "category": "database",
            "status": "ok",
            "value": f"SQLite v{sqlite_version}",
            "details": f"Database connection OK (path: {db_path})",
            "remediation": None,
        }
    except Exception as e:  # noqa: BLE001
        return {
            "name": "SQLite Database & Storage",
            "category": "database",
            "status": "warning",
            "value": "Database check warning",
            "details": f"Failed database probe: {e}",
            "remediation": "Run 'stone db upgrade' to initialize and migrate the database.",
        }


def check_git() -> DiagnosticCheck:
    """Check Git installation and repository status."""
    if not shutil.which("git"):
        return {
            "name": "Git Version Control",
            "category": "vcs",
            "status": "warning",
            "value": "Git not found",
            "details": "Git executable is not available on PATH.",
            "remediation": "Install Git to enable version control and pre-commit hooks.",
        }

    is_git_repo = os.path.isdir(os.path.join(PROJECT_ROOT, ".git"))
    return {
        "name": "Git Version Control",
        "category": "vcs",
        "status": "ok" if is_git_repo else "warning",
        "value": "Repository detected" if is_git_repo else "Not a git repo",
        "details": "Git is installed and repository is initialized."
        if is_git_repo
        else "Project directory is not a Git repository.",
        "remediation": "Run 'git init' to initialize a Git repository."
        if not is_git_repo
        else None,
    }


def run_all_checks() -> list[DiagnosticCheck]:
    """Execute all diagnostic checks."""
    return [
        check_python_version(),
        check_uv(),
        check_bun(),
        check_gui_engine(),
        check_database(),
        check_git(),
    ]


def doctor_command(
    as_json: Annotated[
        bool,
        typer.Option("--json", "-j", help="Output diagnostic report as JSON."),
    ] = False,
) -> None:
    """
    Diagnose environment prerequisites, dependencies, GUI drivers, and database permissions.

    [bold green]Examples:[/bold green]
      [cyan]$ stone doctor[/cyan]                   # Run full environment health check
      [cyan]$ stone doctor --json[/cyan]            # Export diagnostic findings as JSON
    """
    checks = run_all_checks()
    has_errors = any(c["status"] == "error" for c in checks)
    has_warnings = any(c["status"] == "warning" for c in checks)

    if as_json:
        payload: dict[str, Any] = {
            "healthy": not has_errors,
            "has_warnings": has_warnings,
            "checks": checks,
        }
        console.print_json(data=payload)
        if has_errors:
            raise typer.Exit(code=1)
        return

    table = Table(
        title="[bold cyan]Cornerstone Environment & Dependency Diagnostics[/bold cyan]",
        show_header=True,
    )
    table.add_column("Status", justify="center", width=8)
    table.add_column("Check", style="bold", min_width=25)
    table.add_column("Value", style="cyan")
    table.add_column("Details", style="dim")

    for check in checks:
        if check["status"] == "ok":
            status_icon = "[bold green]✓ OK[/bold green]"
        elif check["status"] == "warning":
            status_icon = "[bold yellow]! WARN[/bold yellow]"
        else:
            status_icon = "[bold red]✗ FAIL[/bold red]"

        table.add_row(
            status_icon,
            check["name"],
            check["value"],
            check["details"],
        )

    console.print(table)

    remediations = [c for c in checks if c["remediation"]]
    if remediations:
        console.print("\n[bold yellow]Remediation Recommendations:[/bold yellow]")
        for c in remediations:
            prefix = "[red]✗[/red]" if c["status"] == "error" else "[yellow]![/yellow]"
            console.print(f"  {prefix} [bold]{c['name']}:[/bold] {c['remediation']}")

    if has_errors:
        console.print(
            "\n[bold red]Doctor detected blocking issues that require attention.[/bold red]"
        )
        raise typer.Exit(code=1)
    elif has_warnings:
        console.print(
            "\n[bold yellow]Doctor completed with minor warnings.[/bold yellow]"
        )
    else:
        console.print(
            "\n[bold green]All systems operational! Environment is ready for development.[/bold green]"
        )
