import logging
import os
import sys
import tomllib

DEBUG = False
BASE_PATH = ""
HTML_PATH = ""

if getattr(sys, "frozen", False):
    BASE_PATH = sys._MEIPASS  # PyInstaller temp folder
    DEBUG = False
else:
    BASE_PATH = os.path.dirname(__file__)
    DEBUG = True

if DEBUG:
    HTML_PATH = "http://localhost:5173"  # Dev server
else:
    HTML_PATH = "dist/index.html"  # Bundled files

logging.basicConfig(
    level=logging.INFO if DEBUG else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logging.getLogger("alembic").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def _pyproject_path():
    """Locate pyproject.toml in both dev (project root) and frozen builds.

    In a PyInstaller bundle the file is collected at the bundle root via
    ``--add-data`` (see ``commands/build-pyinstaller.py``).
    """
    if getattr(sys, "frozen", False):
        return os.path.join(BASE_PATH, "pyproject.toml")
    return os.path.join(os.path.dirname(BASE_PATH), "pyproject.toml")


def _load_identity():
    """Read the app's identity from pyproject.toml, the single source of truth.

    ``[project].name``/``version`` provide the package slug and version; the
    human-facing display name comes from ``[tool.app].display-name`` (falling
    back to the slug when unset).
    """
    try:
        with open(_pyproject_path(), "rb") as fh:
            data = tomllib.load(fh)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        logging.getLogger(__name__).warning(
            "Could not read app identity from %s (%s); using fallback values.",
            _pyproject_path(),
            exc,
        )
        data = {}

    project = data.get("project", {})
    slug = project.get("name", "app")
    version = project.get("version", "0.0.0")
    display_name = data.get("tool", {}).get("app", {}).get("display-name") or slug
    return display_name, slug, version


APP_NAME, APP_SLUG, APP_VERSION = _load_identity()

CONFIG = {
    "NAME": APP_NAME,
    "SLUG": APP_SLUG,
    "VERSION": APP_VERSION,
    "DEBUG": DEBUG,
    "BASE_PATH": BASE_PATH,
    "HTML_PATH": HTML_PATH,
}
