"""Git pre-commit hooks manager for automated linting."""

from __future__ import annotations

import os
import stat

import typer
from rich.console import Console

from cli.common import PROJECT_ROOT

console = Console()
hooks_app = typer.Typer(
    name="hooks",
    help="""[bold cyan]Git Pre-Commit Hooks[/bold cyan] - Manage automated linting and code quality hooks.

[bold]Common Workflows:[/bold]
  [cyan]$ stone hooks install[/cyan]                 # Install Git pre-commit hook
  [cyan]$ stone hooks uninstall[/cyan]               # Remove Git pre-commit hook
""",
    rich_markup_mode="rich",
    no_args_is_help=True,
)

PRE_COMMIT_SCRIPT = """#!/usr/bin/env bash
# Cornerstone Pre-Commit Hook
# Automatically runs Ruff and Biome checks on staged files.

set -e

# Identify staged files
STAGED_PY=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\\.py$' || true)
STAGED_JS=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\\.(js|jsx|ts|tsx|vue|json)$' || true)

if [ -z "$STAGED_PY" ] && [ -z "$STAGED_JS" ]; then
    exit 0
fi

echo "[Cornerstone Hooks] Running pre-commit linters on staged files..."

# Python staged check
if [ -n "$STAGED_PY" ]; then
    echo "  → Checking Python with Ruff..."
    uv run ruff check $STAGED_PY
    uv run ruff format --check $STAGED_PY
fi

# Frontend staged check
if [ -n "$STAGED_JS" ]; then
    echo "  → Checking JS/Vue with Biome..."
    bun x biome check $STAGED_JS
fi

echo "[Cornerstone Hooks] ✓ All pre-commit checks passed!"
"""


def get_git_hooks_dir() -> str | None:
    """Resolve the .git/hooks directory if inside a git repo."""
    git_dir = os.path.join(PROJECT_ROOT, ".git")
    if not os.path.exists(git_dir):
        return None
    hooks_dir = os.path.join(git_dir, "hooks")
    os.makedirs(hooks_dir, exist_ok=True)
    return hooks_dir


@hooks_app.command("install", short_help="Install Git pre-commit hook.")
def install_hook() -> None:
    """
    Install Git pre-commit hook to automatically run Ruff and Biome on staged files.

    [bold green]Examples:[/bold green]
      [cyan]$ stone hooks install[/cyan]
      [cyan]$ just setup-hooks[/cyan]
    """
    hooks_dir = get_git_hooks_dir()
    if not hooks_dir:
        console.print(
            "[bold red]Error:[/bold red] Not a Git repository (.git directory missing). Run 'git init' first."
        )
        raise typer.Exit(code=1)

    hook_path = os.path.join(hooks_dir, "pre-commit")
    with open(hook_path, "w", encoding="utf-8") as f:
        f.write(PRE_COMMIT_SCRIPT)

    # Make script executable
    current_stat = os.stat(hook_path)
    os.chmod(
        hook_path, current_stat.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
    )

    console.print(
        f"[bold green]✓[/bold green] Pre-commit hook installed successfully at [magenta]{hook_path}[/magenta]"
    )
    console.print(
        "  [dim]Ruff and Biome will automatically check staged files before each commit.[/dim]"
    )


@hooks_app.command("uninstall", short_help="Remove Git pre-commit hook.")
def uninstall_hook() -> None:
    """
    Remove Git pre-commit hook.

    [bold green]Examples:[/bold green]
      [cyan]$ stone hooks uninstall[/cyan]
    """
    hooks_dir = get_git_hooks_dir()
    if not hooks_dir:
        console.print("[bold red]Error:[/bold red] Not a Git repository.")
        raise typer.Exit(code=1)

    hook_path = os.path.join(hooks_dir, "pre-commit")
    if os.path.exists(hook_path):
        os.remove(hook_path)
        console.print("[bold green]✓[/bold green] Pre-commit hook removed.")
    else:
        console.print("[dim]No pre-commit hook found.[/dim]")
