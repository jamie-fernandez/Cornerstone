"""Rebrand this template into your own application."""

from __future__ import annotations

import argparse
import json
import os
import re

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


def update_docs(display_name: str, slug: str) -> None:
    for rel in DOC_FILES:
        path = os.path.join(PROJECT_ROOT, rel)
        if not os.path.exists(path):
            continue
        text = _read(path)
        text = text.replace(UPSTREAM_URL, "<your-repository-url>")
        text = text.replace("Cornerstone", display_name)
        text = text.replace("cornerstone", slug)
        _write(path, text)


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
) -> None:
    """Rebrand project identity files and optionally clean demo examples."""
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
    update_pyproject(name, slug, desc, aliases=aliases)
    update_package_json(slug, desc)
    update_docs(name, slug)
    if clean_examples_flag:
        clean_examples(name)
        typer.secho(
            "Removed example code (app/api.py demo methods, PMain.vue placeholder).",
            fg=typer.colors.YELLOW,
        )

    seen = set()
    script_names: list[str] = []
    for item in [slug] + [slugify(a) for a in (aliases or []) if slugify(a)]:
        if item and item not in seen:
            seen.add(item)
            script_names.append(item)

    primary_alias = script_names[0]

    typer.secho("\nDone. Next steps:", fg=typer.colors.GREEN, bold=True)
    typer.echo(
        f"  1. {typer.style('just setup', fg=typer.colors.CYAN, bold=True)}        # install dependencies (or python3 -m cli setup)"
    )
    typer.echo(
        f"  2. {typer.style(f'uv run {primary_alias} dev', fg=typer.colors.CYAN, bold=True)}  # run your app (or just dev)"
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
        "  3. Set an app icon and bundle id, choose a LICENSE, and point CI at your repo."
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Rebrand this template into your own application."
    )
    parser.add_argument("name", nargs="+", help='Human-facing app name, e.g. "My App"')
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
    args = parser.parse_args()

    display_name = " ".join(args.name).strip()
    if not display_name:
        parser.error("app name must not be empty")

    rebrand(
        display_name,
        args.description,
        args.clean_examples,
        aliases=args.alias,
    )


if __name__ == "__main__":
    main()
