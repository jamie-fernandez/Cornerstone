"""Rebrand this template into your own application.

Run via ``just init "My App"`` (or ``python commands/init.py "My App"``).

This rewrites the project's identity in one step:
  - ``pyproject.toml``  -> [project].name (slug), version, description,
                           [tool.app].display-name
  - ``package.json``    -> name (slug), version, description
  - docs               -> README.md / AGENTS.md / .zed/README.md prose

``app/config.py`` is intentionally *not* touched: it reads its identity from
pyproject.toml at runtime, so updating pyproject is enough.

Pass ``--clean-examples`` to also strip the placeholder demo code so you start
from a blank slate.
"""

import argparse
import json
import os
import re

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INITIAL_VERSION = "0.1.0"
UPSTREAM_URL = "https://gitlab.com/jnf-desktop-apps/cornerstone"
DOC_FILES = ["README.md", "AGENTS.md", os.path.join(".zed", "README.md")]


def _read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _write(path, text):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def slugify(name):
    """Turn a display name into a PEP 503-style package slug ("My App" -> "my-app")."""
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or "app"


def _toml_escape(value):
    """Escape a string for safe inclusion in a double-quoted TOML value."""
    return value.replace("\\", "\\\\").replace('"', '\\"')


def update_pyproject(display_name, slug, description):
    path = os.path.join(PROJECT_ROOT, "pyproject.toml")
    text = _read(path)
    name_line = f'name = "{_toml_escape(slug)}"'
    version_line = f'version = "{INITIAL_VERSION}"'
    description_line = f'description = "{_toml_escape(description)}"'
    display_line = f'display-name = "{_toml_escape(display_name)}"'
    # Use replacement *functions* so backslashes/quotes in a value are never
    # interpreted as regex replacement escapes (e.g. "\1").
    text = re.sub(r'(?m)^name = ".*"$', lambda _: name_line, text, count=1)
    text = re.sub(r'(?m)^version = ".*"$', lambda _: version_line, text, count=1)
    text = re.sub(r'(?m)^description = ".*"$', lambda _: description_line, text, count=1)
    if re.search(r'(?m)^display-name = ".*"$', text):
        text = re.sub(r'(?m)^display-name = ".*"$', lambda _: display_line, text, count=1)
    else:
        text = text.rstrip() + f"\n\n[tool.app]\n{display_line}\n"
    _write(path, text)


def update_package_json(slug, description):
    path = os.path.join(PROJECT_ROOT, "package.json")
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    data["name"] = slug
    data["version"] = INITIAL_VERSION
    data["description"] = description
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=4)
        fh.write("\n")


def update_docs(display_name, slug):
    for rel in DOC_FILES:
        path = os.path.join(PROJECT_ROOT, rel)
        if not os.path.exists(path):
            continue
        text = _read(path)
        # Replace the upstream repo URL before the slug swap so it isn't mangled.
        text = text.replace(UPSTREAM_URL, "<your-repository-url>")
        text = text.replace("Cornerstone", display_name)
        text = text.replace("cornerstone", slug)
        _write(path, text)


CLEAN_API_PY = '''from app.config import CONFIG
from app.database import SessionLocal, get_db_path, logger
# from app.models import *


class Api:
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


def _clean_pmain(display_name):
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


def clean_examples(display_name):
    _write(os.path.join(PROJECT_ROOT, "app", "api.py"), CLEAN_API_PY)
    _write(os.path.join(PROJECT_ROOT, "ui", "pages", "PMain.vue"), _clean_pmain(display_name))


def main():
    parser = argparse.ArgumentParser(
        description="Rebrand this template into your own application."
    )
    parser.add_argument("name", nargs="+", help='Human-facing app name, e.g. "My App"')
    parser.add_argument("--description", default="", help="Short project description")
    parser.add_argument(
        "--clean-examples",
        action="store_true",
        help="Remove placeholder example code (app/api.py demo methods, PMain.vue)",
    )
    args = parser.parse_args()

    display_name = " ".join(args.name).strip()
    if not display_name:
        parser.error("app name must not be empty")
    slug = slugify(display_name)
    description = args.description or f"{display_name} desktop application"

    print(f"Rebranding template -> {display_name!r} (slug: {slug}, version: {INITIAL_VERSION})")
    update_pyproject(display_name, slug, description)
    update_package_json(slug, description)
    update_docs(display_name, slug)
    if args.clean_examples:
        clean_examples(display_name)
        print("Removed example code (app/api.py demo methods, PMain.vue placeholder).")

    print("\nDone. Next steps:")
    print("  1. just setup        # install dependencies")
    print("  2. just dev          # run your app")
    print("  3. Set an app icon and bundle id, choose a LICENSE, and point CI at your repo.")


if __name__ == "__main__":
    main()
