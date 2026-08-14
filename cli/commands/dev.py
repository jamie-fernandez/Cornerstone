"""Start the development environment: Vite dev server + pywebview backend."""

from __future__ import annotations

import os
import signal
import subprocess
import sys

import typer

from cli.common import BUN_DEFAULT, PROJECT_ROOT, UV_DEFAULT, find_executable

_processes = []


def _shutdown(_signum, _frame):
    typer.secho(
        "\nShutting down development servers...", fg=typer.colors.YELLOW, bold=True
    )
    for proc in _processes:
        proc.terminate()
    for proc in _processes:
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
    sys.exit(0)


def main():
    """Start Vite dev server and backend pywebview process in parallel."""
    os.chdir(PROJECT_ROOT)

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    typer.secho("Starting development environment...", fg=typer.colors.GREEN, bold=True)
    _processes.append(
        subprocess.Popen([find_executable("bun", BUN_DEFAULT), "run", "dev"])
    )
    _processes.append(
        subprocess.Popen([find_executable("uv", UV_DEFAULT), "run", "start.py"])
    )

    for process in _processes:
        process.wait()

    failures = [p.returncode for p in _processes if p.returncode]
    sys.exit(failures[0] if failures else 0)


if __name__ == "__main__":
    main()
