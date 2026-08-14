"""Clean up build artifacts: dist/, build/, ui/dist/, and PyInstaller spec files."""

from __future__ import annotations

import glob
import os
import shutil

import typer
from rich.console import Console

from cli.common import PROJECT_ROOT

console = Console()


def get_build_artifacts() -> list[str]:
    """Find all existing build artifact directories and files."""
    artifacts: list[str] = []

    # Target directories produced by Vite and PyInstaller
    dirs_to_clean = [
        os.path.join(PROJECT_ROOT, "dist"),
        os.path.join(PROJECT_ROOT, "build"),
        os.path.join(PROJECT_ROOT, "ui", "dist"),
    ]
    for dir_path in dirs_to_clean:
        if os.path.exists(dir_path):
            artifacts.append(dir_path)

    # PyInstaller spec files generated in the project root
    for spec_file in glob.glob(os.path.join(PROJECT_ROOT, "*.spec")):
        if os.path.isfile(spec_file):
            artifacts.append(spec_file)

    return sorted(artifacts)


def clean_artifacts(dry_run: bool = False, as_json: bool = False) -> list[str]:
    """Remove all folders and files created by the build command."""
    artifacts = get_build_artifacts()
    rel_artifacts = [os.path.relpath(path, PROJECT_ROOT) for path in artifacts]

    if as_json:
        data = {
            "dry_run": dry_run,
            "artifacts": rel_artifacts,
            "count": len(rel_artifacts),
        }
        console.print_json(data=data)
        if not dry_run:
            for path in artifacts:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                elif os.path.isfile(path):
                    os.remove(path)
        return rel_artifacts

    if not artifacts:
        typer.secho(
            "✓ No build artifacts found to clean.", fg=typer.colors.GREEN, bold=True
        )
        return []

    if dry_run:
        typer.secho(
            "Build artifacts that would be removed:", fg=typer.colors.YELLOW, bold=True
        )
        for rel_path in rel_artifacts:
            typer.secho(f"  - {rel_path}", fg=typer.colors.YELLOW)
        return rel_artifacts

    typer.secho("Cleaning build artifacts...", fg=typer.colors.CYAN, bold=True)
    for path, rel_path in zip(artifacts, rel_artifacts):
        if os.path.isdir(path):
            shutil.rmtree(path)
            typer.secho(f"  ✓ Removed directory: {rel_path}", fg=typer.colors.GREEN)
        elif os.path.isfile(path):
            os.remove(path)
            typer.secho(f"  ✓ Removed file: {rel_path}", fg=typer.colors.GREEN)

    typer.secho(
        f"✓ Clean complete! ({len(artifacts)} artifact(s) removed)",
        fg=typer.colors.GREEN,
        bold=True,
    )
    return rel_artifacts


def main() -> None:
    """Execute clean command."""
    clean_artifacts()


if __name__ == "__main__":
    main()
