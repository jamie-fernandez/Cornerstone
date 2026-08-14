"""Development environment setup: installs Bun, UV, and dependencies."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys

import typer

from cli.common import PROJECT_ROOT


def check_command(command: str) -> bool:
    """Check if a command is available in the system."""
    return shutil.which(command) is not None


def install_bun() -> bool:
    """Install Bun.js based on the operating system."""
    typer.echo("\n")
    typer.secho("╭─────────────────────────────────────────╮", fg=typer.colors.CYAN)
    typer.secho(
        "│  Installing Bun.js...                   │", fg=typer.colors.CYAN, bold=True
    )
    typer.secho("╰─────────────────────────────────────────╯\n", fg=typer.colors.CYAN)

    try:
        if sys.platform in ("darwin", "linux"):
            subprocess.run(
                "curl -fsSL https://bun.sh/install | bash",
                shell=True,
                check=True,
            )
        elif sys.platform == "win32":
            subprocess.run(
                'powershell -c "irm bun.sh/install.ps1 | iex"',
                shell=True,
                check=True,
            )
        typer.secho(
            "✓ Bun.js installed successfully\n", fg=typer.colors.GREEN, bold=True
        )
        return True
    except subprocess.CalledProcessError as e:
        typer.secho(f"✗ Failed to install Bun.js: {e}", fg=typer.colors.RED, bold=True)
        return False


def install_uv() -> bool:
    """Install UV based on the operating system."""
    typer.echo("\n")
    typer.secho("╭─────────────────────────────────────────╮", fg=typer.colors.CYAN)
    typer.secho(
        "│  Installing UV...                       │", fg=typer.colors.CYAN, bold=True
    )
    typer.secho("╰─────────────────────────────────────────╯\n", fg=typer.colors.CYAN)

    try:
        if sys.platform in ("darwin", "linux"):
            subprocess.run(
                "curl -LsSf https://astral.sh/uv/install.sh | sh",
                shell=True,
                check=True,
            )
        elif sys.platform == "win32":
            subprocess.run(
                'powershell -c "irm https://astral.sh/uv/install.ps1 | iex"',
                shell=True,
                check=True,
            )
        typer.secho("✓ UV installed successfully\n", fg=typer.colors.GREEN, bold=True)
        return True
    except subprocess.CalledProcessError as e:
        typer.secho(f"✗ Failed to install UV: {e}", fg=typer.colors.RED, bold=True)
        return False


def setup() -> None:
    """Main setup function to initialize the development environment."""
    try:
        typer.echo("\n")
        typer.secho(
            "╔═══════════════════════════════════════════╗",
            fg=typer.colors.CYAN,
            bold=True,
        )
        typer.secho(
            "║  Development Environment Setup            ║",
            fg=typer.colors.CYAN,
            bold=True,
        )
        typer.secho(
            "╚═══════════════════════════════════════════╝\n",
            fg=typer.colors.CYAN,
            bold=True,
        )

        os.chdir(PROJECT_ROOT)

        # Check and install Bun if needed
        bun_path = "bun"
        if not check_command("bun"):
            typer.secho(
                "⚠ Bun.js not found. Installing...", fg=typer.colors.YELLOW, bold=True
            )
            if not install_bun():
                typer.secho(
                    "✗ Bun installation failed. Please install manually: https://bun.sh",
                    fg=typer.colors.RED,
                    bold=True,
                )
                sys.exit(1)
            # Try to find bun in its default installation path
            home = os.path.expanduser("~")
            potential_bun = os.path.join(home, ".bun", "bin", "bun")
            if os.path.exists(potential_bun):
                bun_path = potential_bun
        else:
            typer.secho("✓ Bun.js is already installed\n", fg=typer.colors.GREEN)

        # Check and install UV if needed
        uv_path = "uv"
        if not check_command("uv"):
            typer.secho(
                "⚠ UV not found. Installing...", fg=typer.colors.YELLOW, bold=True
            )
            if not install_uv():
                typer.secho(
                    "✗ UV installation failed. Please install manually: https://docs.astral.sh/uv/getting-started/installation/",
                    fg=typer.colors.RED,
                    bold=True,
                )
                sys.exit(1)
            # Try to find uv in its default installation path
            home = os.path.expanduser("~")
            potential_uv = os.path.join(home, ".local", "bin", "uv")
            if os.path.exists(potential_uv):
                uv_path = potential_uv
        else:
            typer.secho("✓ UV is already installed\n", fg=typer.colors.GREEN)

        # Install Node dependencies with Bun
        typer.secho("╭─────────────────────────────────────────╮", fg=typer.colors.CYAN)
        typer.secho(
            "│  Installing frontend dependencies...    │",
            fg=typer.colors.CYAN,
            bold=True,
        )
        typer.secho(
            "╰─────────────────────────────────────────╯\n", fg=typer.colors.CYAN
        )
        subprocess.run([bun_path, "install"], check=True)
        typer.secho(
            "\n✓ Frontend dependencies installed\n", fg=typer.colors.GREEN, bold=True
        )

        # Install Python dependencies with UV
        typer.secho("╭─────────────────────────────────────────╮", fg=typer.colors.CYAN)
        typer.secho(
            "│  Installing Python dependencies...      │",
            fg=typer.colors.CYAN,
            bold=True,
        )
        typer.secho(
            "╰─────────────────────────────────────────╯\n", fg=typer.colors.CYAN
        )
        subprocess.run([uv_path, "sync"], check=True)
        typer.secho(
            "\n✓ Python dependencies installed\n", fg=typer.colors.GREEN, bold=True
        )

        typer.secho(
            "╭─────────────────────────────────────────╮",
            fg=typer.colors.GREEN,
            bold=True,
        )
        typer.secho(
            "│  Setup Complete!                        │",
            fg=typer.colors.GREEN,
            bold=True,
        )
        typer.secho(
            "╰─────────────────────────────────────────╯\n",
            fg=typer.colors.GREEN,
            bold=True,
        )
        typer.echo(
            f'You can now run "{typer.style("uv run stone dev", fg=typer.colors.CYAN, bold=True)}" or activate your venv.'
        )
        typer.echo("\nCLI invocation options:")
        typer.echo(
            f"  • With UV:           {typer.style('uv run stone dev', fg=typer.colors.CYAN)}"
        )
        typer.echo(
            f"  • Active venv:       {typer.style('stone dev', fg=typer.colors.CYAN)}"
        )
        typer.echo(
            f"  • Global tool:       {typer.style('uv tool install --editable .', fg=typer.colors.CYAN)}"
        )
    except subprocess.CalledProcessError as e:
        typer.secho(
            f"✗ An error occurred during setup: {e}", fg=typer.colors.RED, bold=True
        )
        sys.exit(1)
    except Exception as e:  # noqa: BLE001 - top-level CLI guard: report any failure and exit
        typer.secho(
            f"✗ An unexpected error occurred: {e}", fg=typer.colors.RED, bold=True
        )
        sys.exit(1)


if __name__ == "__main__":
    setup()
