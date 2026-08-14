"""Build production assets: the Vite frontend bundle, then the PyInstaller executable."""

from __future__ import annotations

import os
import subprocess
import sys

import typer

from cli.common import BUN_DEFAULT, PROJECT_ROOT, UV_DEFAULT, find_executable

BUILD_STEPS = [
    ("frontend", [find_executable("bun", BUN_DEFAULT), "run", "vite", "build"]),
    (
        "backend executable",
        [
            find_executable("uv", UV_DEFAULT),
            "run",
            "-m",
            "cli.commands.build_pyinstaller",
        ],
    ),
]


def main() -> None:
    """Execute all build steps sequentially."""
    os.chdir(PROJECT_ROOT)

    typer.secho("Building production assets...", fg=typer.colors.CYAN, bold=True)
    try:
        for label, cmd in BUILD_STEPS:
            typer.secho(f"Building {label}...", fg=typer.colors.BLUE, bold=True)
            subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        typer.secho(
            f"✗ Build failed: {' '.join(e.cmd)} exited with code {e.returncode}",
            fg=typer.colors.RED,
            bold=True,
        )
        sys.exit(1)

    typer.secho(
        "✓ Build complete! Check the 'dist' directory.",
        fg=typer.colors.GREEN,
        bold=True,
    )


if __name__ == "__main__":
    main()
