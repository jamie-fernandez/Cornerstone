"""PyInstaller packaging helper for Cornerstone."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys

import typer

from cli.common import PROJECT_ROOT


def build_app():
    """Build the standalone desktop executable with PyInstaller."""
    typer.secho("Starting PyInstaller build...", fg=typer.colors.CYAN, bold=True)

    if PROJECT_ROOT not in sys.path:
        sys.path.insert(0, PROJECT_ROOT)
    from app.config import CONFIG

    ui_dist_dir = os.path.join(PROJECT_ROOT, "ui", "dist")
    app_path = os.path.join(PROJECT_ROOT, "start.py")
    pyproject_path = os.path.join(PROJECT_ROOT, "pyproject.toml")
    alembic_ini_path = os.path.join(PROJECT_ROOT, "alembic.ini")
    migrations_dir = os.path.join(PROJECT_ROOT, "app", "migrations")

    dist_dir = os.path.join(PROJECT_ROOT, "dist")
    build_dir = os.path.join(PROJECT_ROOT, "build")

    # Verify UI dist directory exists
    if not os.path.exists(ui_dist_dir):
        typer.secho(
            f"ERROR: UI dist directory not found at {ui_dist_dir}",
            fg=typer.colors.RED,
            bold=True,
        )
        typer.secho(
            "Please run 'bun run vite build' first to build the Vue app.",
            fg=typer.colors.YELLOW,
        )
        return

    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)

    # Determine the correct path separator for --add-data based on OS
    separator = ";" if os.name == "nt" else ":"

    args = [
        "pyinstaller",
        "--windowed",
        "--clean",
        "--add-data",
        f"{ui_dist_dir}{separator}ui/dist",
        # Bundle pyproject.toml so the frozen app can read its own identity.
        "--add-data",
        f"{pyproject_path}{separator}.",
        # Bundle Alembic configuration and migration scripts.
        "--add-data",
        f"{alembic_ini_path}{separator}.",
        "--add-data",
        f"{migrations_dir}{separator}app/migrations",
        "--hidden-import",
        "alembic",
        "--name",
        CONFIG["NAME"],
        app_path,
    ]

    subprocess.run(args, check=True)

    typer.secho(
        f"✓ PyInstaller build complete: {CONFIG['NAME']}",
        fg=typer.colors.GREEN,
        bold=True,
    )


if __name__ == "__main__":
    build_app()
