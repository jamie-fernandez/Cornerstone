"""Rebrand this template into your own application."""

from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import shutil
import subprocess

import typer

from cli.common import PROJECT_ROOT

INITIAL_VERSION = "0.1.0"
UPSTREAM_URL = "https://gitlab.com/jnf-desktop-apps/cornerstone"
DOC_FILES = ["README.md", "AGENTS.md", os.path.join(".zed", "README.md")]


def _read(path: str) -> str:
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _write(path: str, text: str) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def slugify(name: str) -> str:
    """Turn a display name into a PEP 503-style package slug ("My App" -> "my-app")."""
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or "app"


def _toml_escape(value: str) -> str:
    """Escape a string for safe inclusion in a double-quoted TOML value."""
    return value.replace("\\", "\\\\").replace('"', '\\"')


def update_pyproject(
    display_name: str,
    slug: str,
    description: str,
    aliases: list[str] | None = None,
) -> None:
    path = os.path.join(PROJECT_ROOT, "pyproject.toml")
    text = _read(path)
    name_line = f'name = "{_toml_escape(slug)}"'
    version_line = f'version = "{INITIAL_VERSION}"'
    description_line = f'description = "{_toml_escape(description)}"'
    display_line = f'display-name = "{_toml_escape(display_name)}"'
    text = re.sub(r'(?m)^name = ".*"$', lambda _: name_line, text, count=1)
    text = re.sub(r'(?m)^version = ".*"$', lambda _: version_line, text, count=1)
    text = re.sub(
        r'(?m)^description = ".*"$', lambda _: description_line, text, count=1
    )

    if re.search(r'(?m)^display-name = ".*"$', text):
        text = re.sub(
            r'(?m)^display-name = ".*"$', lambda _: display_line, text, count=1
        )
    else:
        text = text.rstrip() + f"\n\n[tool.app]\n{display_line}\n"

    seen = set()
    script_names: list[str] = []
    for item in [slug] + [slugify(a) for a in (aliases or []) if slugify(a)]:
        if item and item not in seen:
            seen.add(item)
            script_names.append(item)

    scripts_section = "[project.scripts]\n" + "\n".join(
        f'{_toml_escape(name)} = "cli:app"' for name in script_names
    )
    if re.search(r"(?ms)^\[project\.scripts\].*?(?=\n\[|\Z)", text):
        text = re.sub(
            r"(?ms)^\[project\.scripts\].*?(?=\n\[|\Z)",
            lambda _: scripts_section,
            text,
            count=1,
        )
    else:
        text = text.rstrip() + f"\n\n{scripts_section}\n"

    _write(path, text)


def update_package_json(slug: str, description: str) -> None:
    path = os.path.join(PROJECT_ROOT, "package.json")
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    data["name"] = slug
    data["version"] = INITIAL_VERSION
    data["description"] = description
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=4)
        fh.write("\n")


def archive_template_docs(display_name: str, slug: str) -> None:
    """Archive original Cornerstone template documentation into .cornerstone/ folder."""
    cornerstone_dir = os.path.join(PROJECT_ROOT, ".cornerstone")
    os.makedirs(cornerstone_dir, exist_ok=True)

    # Copy template README.md if not already archived
    src_readme = os.path.join(PROJECT_ROOT, "README.md")
    dest_readme = os.path.join(cornerstone_dir, "README.md")
    if os.path.exists(src_readme) and not os.path.exists(dest_readme):
        shutil.copyfile(src_readme, dest_readme)

    # Copy template AGENTS.md if not already archived
    src_agents = os.path.join(PROJECT_ROOT, "AGENTS.md")
    dest_agents = os.path.join(cornerstone_dir, "AGENTS.md")
    if os.path.exists(src_agents) and not os.path.exists(dest_agents):
        shutil.copyfile(src_agents, dest_agents)

    # Write UPSTREAM.md
    now_str = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d %H:%M:%S UTC")
    upstream_content = f"""# Upstream Template Information

- **Template:** Cornerstone Desktop Application Template
- **Upstream Repository:** {UPSTREAM_URL}
- **Template Version:** 0.1.0
- **Scaffolded Application:** {display_name} (`{slug}`)
- **Scaffolded Date:** {now_str}

## About Cornerstone
Cornerstone is a cross-platform desktop application template using Vue.js for the frontend and Python for the backend, bridged via `pywebview`.
The original template documentation, bridge architectural specifications, and agent guidelines are preserved in this `.cornerstone/` directory.

## Updating from Upstream
To inspect upstream updates or compare changes:
- Git Remote: `{UPSTREAM_URL}`
"""
    _write(os.path.join(cornerstone_dir, "UPSTREAM.md"), upstream_content)


def generate_app_readme(
    display_name: str, slug: str, description: str, primary_alias: str
) -> None:
    """Generate a clean application-specific README.md for the newly rebranded project."""
    readme_path = os.path.join(PROJECT_ROOT, "README.md")
    desc_text = description or f"{display_name} desktop application."

    content = f"""# {display_name}

{desc_text}

Package: `{slug}`

## Overview

{display_name} is a cross-platform desktop application built with [Vue.js 3](https://vuejs.org/), [Vuetify 3](https://vuetifyjs.com/), [Tailwind CSS 4](https://tailwindcss.com/), and [Python 3.13+](https://www.python.org/) using [pywebview](https://pywebview.flowrl.com/).

## Getting Started

### 1. Setup Development Environment

Install dependencies and configure virtual environments:

```bash
just setup
# or
{primary_alias} setup
```

### 2. Start the Application

Launch in development mode with hot-reloading for both frontend and backend:

```bash
just dev
# or
{primary_alias} dev
```

### 3. Diagnostics & Health Check

Verify your development environment prerequisites and GUI drivers:

```bash
{primary_alias} doctor
```

### 4. Build Production Executable

Package the standalone executable for your operating system:

```bash
just build
# or
{primary_alias} build
```

## Available Commands

| Command | Purpose |
|:---|:---|
| `just setup` / `{primary_alias} setup` | Install Bun/UV and sync project dependencies. |
| `just dev` / `{primary_alias} dev` | Start development servers and open desktop window. |
| `just test` / `{primary_alias} test` | Run backend, CLI, and frontend test suites. |
| `just lint` / `just lint-fix` | Lint and auto-format code with Biome and Ruff. |
| `{primary_alias} make api <name>` | Scaffold a new bridge API method and mock. |
| `{primary_alias} make page <name>` | Scaffold a new Vue page and register route. |
| `{primary_alias} make model <name>` | Scaffold an SQLAlchemy database model. |
| `{primary_alias} doctor` | Run system and environment diagnostics. |
| `just build` / `{primary_alias} build` | Build production assets and standalone executable. |

## Template Documentation

The original Cornerstone template documentation and bridge architecture guides are archived in the [`.cornerstone/`](.cornerstone/) directory.
"""
    _write(readme_path, content)


def update_docs(
    display_name: str, slug: str, description: str = "", primary_alias: str = "stone"
) -> None:
    archive_template_docs(display_name, slug)
    generate_app_readme(display_name, slug, description, primary_alias)

    # Update AGENTS.md if it exists
    agents_path = os.path.join(PROJECT_ROOT, "AGENTS.md")
    if os.path.exists(agents_path):
        text = _read(agents_path)
        text = text.replace(UPSTREAM_URL, "<your-repository-url>")
        text = text.replace("Cornerstone", display_name)
        text = text.replace("cornerstone", slug)
        _write(agents_path, text)

    # Update any other doc files
    for rel in DOC_FILES:
        if rel in ("README.md", "AGENTS.md"):
            continue
        path = os.path.join(PROJECT_ROOT, rel)
        if not os.path.exists(path):
            continue
        text = _read(path)
        text = text.replace(UPSTREAM_URL, "<your-repository-url>")
        text = text.replace("Cornerstone", display_name)
        text = text.replace("cornerstone", slug)
        _write(path, text)


def configure_ci_workflows(ci_preference: str) -> None:
    """Configure CI workflows based on user preference ('both', 'github', 'gitlab')."""
    pref = ci_preference.lower().strip()
    github_dir = os.path.join(PROJECT_ROOT, ".github")
    gitlab_ci_file = os.path.join(PROJECT_ROOT, ".gitlab-ci.yml")
    gitlab_dir = os.path.join(PROJECT_ROOT, ".gitlab")

    if pref == "github":
        if os.path.exists(gitlab_ci_file):
            os.remove(gitlab_ci_file)
        if os.path.exists(gitlab_dir):
            shutil.rmtree(gitlab_dir, ignore_errors=True)
        typer.secho(
            "✓ Configured GitHub Actions CI (removed GitLab CI configs).",
            fg=typer.colors.GREEN,
        )
    elif pref == "gitlab":
        if os.path.exists(github_dir):
            shutil.rmtree(github_dir, ignore_errors=True)
        typer.secho(
            "✓ Configured GitLab CI (removed GitHub Actions workflows).",
            fg=typer.colors.GREEN,
        )
    else:
        typer.secho(
            "✓ Retained dual CI workflows (GitHub Actions & GitLab CI).",
            fg=typer.colors.GREEN,
        )


def reinitialize_git_repository(display_name: str) -> None:
    """Re-initialize a fresh Git repository and create the initial commit."""
    git_dir = os.path.join(PROJECT_ROOT, ".git")
    if os.path.exists(git_dir):
        shutil.rmtree(git_dir, ignore_errors=True)

    try:
        subprocess.run(
            ["git", "init"], cwd=PROJECT_ROOT, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "add", "."], cwd=PROJECT_ROOT, check=True, capture_output=True
        )
        subprocess.run(
            [
                "git",
                "commit",
                "-m",
                f"Initial commit for {display_name} from Cornerstone template",
            ],
            cwd=PROJECT_ROOT,
            check=True,
            capture_output=True,
        )
        typer.secho(
            "✓ Re-initialized fresh Git repository with initial commit.",
            fg=typer.colors.GREEN,
            bold=True,
        )
    except Exception as e:  # noqa: BLE001
        typer.secho(f"⚠ Git re-initialization warning: {e}", fg=typer.colors.YELLOW)


CLEAN_API_PY = '''from app.config import CONFIG
from app.database import SessionLocal, get_db_path, logger
# from app.models import *


class API:
    """Python API class that can be called from JavaScript"""

    def __init__(self):
        self._window = None

    def set_window(self, window):
        self._window = window

    def quit(self):
        # Use hide() if you plan to reuse the window; use destroy() when you're done with it entirely.
        self._window.hide()

    def get_app_configuration(self):
        return CONFIG

    def get_database_path(self):
        """Get current database path"""
        return {"path": get_db_path()}

    def test_database_connection(self):
        """Test database connection"""
        from sqlalchemy import text

        try:
            with SessionLocal() as db:
                db.execute(text("SELECT 1"))
            return {"status": "success", "message": "Database connection OK"}
        except Exception as e:
            logger.error(f"Database test failed: {e}")
            return {"status": "error", "message": str(e)}
'''


def _clean_pmain(display_name: str) -> str:
    return (
        "<script setup>\n\n</script>\n\n"
        "<template>\n"
        "    <v-main>\n"
        "        <v-container>\n"
        f"            {display_name}\n"
        "        </v-container>\n"
        "    </v-main>\n"
        "</template>\n"
    )


def clean_examples(display_name: str) -> None:
    _write(os.path.join(PROJECT_ROOT, "app", "api.py"), CLEAN_API_PY)
    _write(
        os.path.join(PROJECT_ROOT, "ui", "pages", "PMain.vue"),
        _clean_pmain(display_name),
    )


def rebrand(
    display_name: str,
    description: str = "",
    clean_examples_flag: bool = False,
    aliases: list[str] | None = None,
    ci: str = "both",
    fresh_git: bool = False,
) -> None:
    """Rebrand project identity files, archive template docs, and configure options."""
    name = display_name.strip()
    if not name:
        raise ValueError("App name must not be empty")
    slug = slugify(name)
    desc = description or f"{name} desktop application"

    typer.secho(
        f"Rebranding template -> {name!r} (slug: {slug}, version: {INITIAL_VERSION})",
        fg=typer.colors.CYAN,
        bold=True,
    )

    seen = set()
    script_names: list[str] = []
    for item in [slug] + [slugify(a) for a in (aliases or []) if slugify(a)]:
        if item and item not in seen:
            seen.add(item)
            script_names.append(item)

    primary_alias = script_names[0]

    update_pyproject(name, slug, desc, aliases=aliases)
    update_package_json(slug, desc)
    update_docs(name, slug, desc, primary_alias=primary_alias)

    if ci:
        configure_ci_workflows(ci)

    if clean_examples_flag:
        clean_examples(name)
        typer.secho(
            "Removed example code (app/api.py demo methods, PMain.vue placeholder).",
            fg=typer.colors.YELLOW,
        )

    if fresh_git:
        reinitialize_git_repository(name)

    typer.secho("\nDone. Next steps:", fg=typer.colors.GREEN, bold=True)
    typer.echo(
        f"  1. {typer.style('just setup', fg=typer.colors.CYAN, bold=True)}        # install dependencies (or stone setup)"
    )
    typer.echo(
        f"  2. {typer.style(f'{primary_alias} doctor', fg=typer.colors.CYAN, bold=True)}      # verify system dependencies & GUI drivers"
    )
    typer.echo(
        f"  3. {typer.style(f'uv run {primary_alias} dev', fg=typer.colors.CYAN, bold=True)}  # run your app (or just dev)"
    )
    typer.echo(
        f"     Direct CLI: {typer.style(f'{primary_alias} dev', fg=typer.colors.CYAN)} (when venv active) or {typer.style('uv tool install --editable .', fg=typer.colors.CYAN)}"
    )

    if len(script_names) > 1:
        alias_list = ", ".join(script_names)
        typer.echo(
            f"     Registered CLI commands: {typer.style(alias_list, fg=typer.colors.MAGENTA)}"
        )
    typer.echo(
        "  4. Set an app icon and bundle id, choose a LICENSE, and point CI at your repo."
    )


def interactive_wizard() -> tuple[str, str, list[str], bool, str, bool]:
    """Interactive CLI wizard for rebranding the template."""
    typer.secho(
        "\n✨ Cornerstone Interactive Rebranding Wizard ✨\n",
        fg=typer.colors.CYAN,
        bold=True,
    )

    default_name = (
        os.path.basename(os.path.abspath(PROJECT_ROOT)).replace("-", " ").title()
    )
    app_name = typer.prompt("Application Display Name", default=default_name)
    slug = slugify(app_name)
    typer.echo(f"  → Package slug: {slug}")

    description = typer.prompt("Description", default=f"{app_name} desktop application")
    alias_input = typer.prompt(
        "Command Line Aliases (comma-separated, optional)", default="stone"
    )
    aliases = [a.strip() for a in alias_input.split(",") if a.strip()]

    typer.echo("\nCI/CD Platform Preference:")
    typer.echo("  [1] Both GitHub Actions and GitLab CI")
    typer.echo("  [2] GitHub Actions only")
    typer.echo("  [3] GitLab CI only")
    ci_choice = typer.prompt("Select CI/CD option", default="1")
    ci_map = {"1": "both", "2": "github", "3": "gitlab"}
    ci_val = ci_map.get(ci_choice, "both")

    fresh_git = typer.confirm(
        "Re-initialize fresh Git repository with initial commit?", default=False
    )
    clean_ex = typer.confirm("Remove demo example code (clean slate)?", default=False)

    return app_name, description, aliases, clean_ex, ci_val, fresh_git


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Rebrand this template into your own application."
    )
    parser.add_argument("name", nargs="*", help='Human-facing app name, e.g. "My App"')
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Run interactive rebranding wizard",
    )
    parser.add_argument(
        "--description", "-d", default="", help="Short project description"
    )
    parser.add_argument(
        "--alias",
        "-a",
        action="append",
        default=[],
        help="Custom CLI command alias(es) (e.g. -a stone)",
    )
    parser.add_argument(
        "--clean-examples",
        action="store_true",
        help="Remove placeholder example code (app/api.py demo methods, PMain.vue)",
    )
    parser.add_argument(
        "--ci",
        choices=["both", "github", "gitlab"],
        default="both",
        help="CI/CD workflows to retain ('both', 'github', 'gitlab')",
    )
    parser.add_argument(
        "--fresh-git",
        "--reset-git",
        action="store_true",
        dest="fresh_git",
        help="Re-initialize fresh Git repository with a clean initial commit",
    )
    args = parser.parse_args()

    if args.interactive or not args.name:
        display_name, desc, aliases, clean_ex, ci_val, fresh_git = interactive_wizard()
        rebrand(
            display_name,
            desc,
            clean_ex,
            aliases=aliases,
            ci=ci_val,
            fresh_git=fresh_git,
        )
        return

    display_name = " ".join(args.name).strip()
    if not display_name:
        parser.error("app name must not be empty")

    rebrand(
        display_name,
        args.description,
        args.clean_examples,
        aliases=args.alias,
        ci=args.ci,
        fresh_git=args.fresh_git,
    )


if __name__ == "__main__":
    main()
