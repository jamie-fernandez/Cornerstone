# Cornerstone

A template repository for building cross-platform desktop applications for macOS, Linux, and Windows using Vue.js and Python.

## Overview

Cornerstone provides a robust starting point for desktop application development by combining a modern Vue.js frontend with a powerful Python backend, unified through the `pywebview` library. It leverages high-performance package managers and development tools to ensure a smooth developer experience.

### Tech Stack

- **Frontend:** [Vue.js 3](https://vuejs.org/) with [Vite](https://vitejs.dev/)
- **UI Framework:** [Vuetify 3](https://vuetifyjs.com/) & [Tailwind CSS 4](https://tailwindcss.com/)
- **Backend:** [Python 3.13+](https://www.python.org/)
- **Desktop Bridge:** [pywebview](https://pywebview.flowrl.com/)
- **Database:** [SQLAlchemy](https://www.sqlalchemy.org/) (SQLite by default)
- **Package Managers:** [Bun](https://bun.sh/) & [UV](https://docs.astral.sh/uv/) (Python). **Note:** We use `uv` for all Python dependency management and execution. Do not use `pip`.
- **Code Quality:** [Biome](https://biomejs.dev/) (JS/TS) & [Ruff](https://docs.astral.sh/ruff/) (Python)
- **Testing:** [Vitest](https://vitest.dev/) (Unit), [Pytest](https://pytest.org/) (Backend), [Cypress](https://www.cypress.io/) (E2E)

## Requirements

- **Python:** 3.13 or higher
- **Bun:** (Will be auto-installed by setup if missing)
- **UV:** (Will be auto-installed by setup if missing)

## Make It Your Own

After forking, rebrand the template into your own application in one step:

```bash
just init "My App"                       # rename everything; reset version to 0.1.0
just init "My App" --alias stone -a app  # register custom shorthand CLI aliases
just init "My App" --clean-examples      # also strip placeholder/demo code
```

This rewrites the project name, slug, version, description, and CLI entry points (`[project.scripts]`)
in `pyproject.toml` and `package.json`, and updates the docs. The app's identity (window title, built
executable name, macOS bundle) is derived at runtime from `[tool.app] display-name`
and `[project] name`/`version` in `pyproject.toml` — the single source of truth — so
there is nothing else to hand-edit. Afterwards, set an app icon and bundle id,
choose a `LICENSE`, and point CI at your own repository.

## Getting Started

### 1. Setup Development Environment

Run the following command to install all dependencies and configure virtual environments:

```bash
python3 -m cli setup
```

**What this does:**
- Checks for and installs **Bun.js** and **UV** if they are missing.
- Installs frontend dependencies using `bun install`.
- Installs Python dependencies and creates a virtual environment using `uv sync`.

### 2. Start the Application

To launch the application in development mode with hot-reload enabled for both frontend and backend:

```bash
python3 -m cli dev
```

### ⚡ Using Just (Recommended)

If you have [just](https://github.com/casey/just) installed, you can use these shortcuts:

```bash
just setup    # Initialize the environment
just dev      # Start development mode
just test     # Run all tests
just lint     # Run linters
just build    # Build for production
```

**What to expect:**
- The Vite development server starts for the Vue frontend.
- The Python backend launches and opens a `pywebview` window.
- The application window will appear, loading the frontend from the dev server.

## Available Commands

| Command                | Purpose                                                                     |
|:-----------------------|:----------------------------------------------------------------------------|
| `just setup`           | Initialize the development environment and dependencies.                    |
| `just dev`             | Start both frontend and backend in development mode.                        |
| `just cli`             | Run the application Typer CLI (e.g. `just cli --help`, `just cli db info`). |
| `just build`           | Build the production assets for both frontend and backend.                  |
| `just clean`           | Clean up build artifacts and temporary files.                               |
| `bun run dev`          | Start only the Vite development server (frontend).                          |
| `bun run test:ui:unit` | Run frontend unit tests using Vitest.                                       |
| `just test-app`        | Run backend unit tests using Pytest.                                        |
| `bun run test:ui:e2e`  | Run end-to-end tests using Cypress.                                         |
| `bun run lint:fix`     | Run Biome to check and fix code formatting/linting.                         |
| `just build-win`       | Package the application as a Windows executable.                            |
| `just build-mac`       | Package the application as a macOS bundle.                                  |

### Command Line Interface (CLI)

Cornerstone includes a built-in Typer CLI (`cli` package) with rich formatting for interacting with application
services, development tools, browsing internal CLI documentation, and managing the SQLite database.

You can invoke the CLI through several flexible methods:

- **Default Scripts:** `uv run stone <command>` or `uv run cornerstone <command>`
- **Active Virtualenv:** `stone <command>` (when `.venv` is activated)
- **Global Tool:** `uv tool install --editable .` allows running `stone` / `cornerstone` anywhere on your machine
- **Command Runner:** `just cli <command>`

```bash
uv run stone --help             # View all CLI commands and workflows
uv run stone docs               # Browse interactive CLI documentation guide
uv run stone docs db            # View detailed documentation for database commands
uv run stone docs init --markdown # Output command guide in Markdown format
uv run stone info               # Display app details and runtime configuration
uv run stone stats              # Display system metrics and resource usage
uv run stone clean              # Clean up build artifacts (dist, build, ui/dist, *.spec)
uv run stone db info            # Inspect SQLite database status, size, and tables
uv run stone db test            # Test database connectivity
uv run stone db init            # Initialize schema and run migrations
uv run stone db migrate -m "create_users_table" # Generate a new sequential migration revision
uv run stone db upgrade         # Apply pending migrations to head
uv run stone db downgrade       # Revert previous migration revision
uv run stone db current         # Inspect current migration revision (e.g. 0001)
uv run stone db history         # View chronological migration history
uv run stone db tables          # List database schema and column details
uv run stone db query "SELECT 1"# Run a raw SQL query (supports --json)
uv run stone db reset --yes     # Reset and re-create database file
```

## Project Structure

```text
cornerstone/
├── alembic.ini         # Alembic migration configuration
├── app/                # Python Backend
│   ├── api.py          # JS-exposed API classes
│   ├── config.py       # Backend configuration
│   ├── database.py     # Database & SQLAlchemy setup
│   ├── migrations/     # Database schema migrations & versions
│   ├── models.py       # Database models
│   └── __tests__/      # Backend unit tests
├── cli/                # Application CLI and Developer Tools
│   ├── commands/       # CLI command implementations (build, clean, dev, init, setup, db)
│   ├── common.py       # Shared CLI helpers & executable resolution
│   ├── main.py         # Typer application definition
│   └── __tests__/      # CLI unit tests
├── ui/                 # Vue.js Frontend
│   ├── App.vue         # Root Vue component
│   ├── main.js         # Frontend entry point
│   ├── pages/          # Vue page components
│   ├── stores/         # Pinia state management
│   ├── utils/          # Python bridge client & shared helpers
│   └── __tests__/      # Frontend unit tests
├── cypress/            # End-to-end tests
├── dist/               # Production build output
├── index.html          # Vite entry HTML
├── pyproject.toml      # Python project configuration
├── package.json        # Frontend project configuration
└── start.py            # Main application entry point (Python)
```

## Environment Variables

Currently, the project uses a centralized configuration in `app/config.py`.

- **TODO:** Implement support for `.env` files if environment-specific overrides are needed.

## Testing

### Frontend Unit Tests
```bash
bun run test:ui:unit
```

### Backend Unit Tests
```bash
just test-app
```

### End-to-End Tests
```bash
bun run test:ui:e2e
```

### GitLab CI

Pipelines run lint (Ruff/Biome + `pip-audit`), unit tests with coverage reports (JUnit + Cobertura surfaced in Merge Requests), Cypress E2E, per-OS dry-run builds, and GitLab's Secret-Detection/SAST security scans. Jobs cache dependencies keyed on the lockfiles and skip when a change doesn't touch their stack; scheduled pipelines run Renovate only. Pushing a version tag (e.g. `v0.2.0`) runs the release build and creates a GitLab Release with the Linux bundle attached.

To test and debug GitLab CI pipelines locally, it is recommended to use [gitlab-ci-local](https://github.com/firecow/gitlab-ci-local).

## GitLab Labels

| Label                  | Description                                                                              |
|------------------------|------------------------------------------------------------------------------------------|
| frontend               | Changes related to the Vue.js frontend (ui/ directory).                                  |
| backend                | Changes related to the Python backend (app/ directory or start.py file).                 |
| feature                | A new feature for the user; aligns with a MINOR version bump in semver.                  |
| fix                    | A bug fix for the user; aligns with a PATCH version bump in semver.                      |
| breaking-change        | A change that breaks backward compatibility; aligns with a MAJOR version bump in semver. |
| documentation          | Changes to documentation only, with no effect on code behavior.                          |
| style                  | Formatting or whitespace changes that don't affect code logic.                           |
| refactor               | A code change that neither fixes a bug nor adds a feature.                               |
| performance            | A code change that improves performance.                                                 |
| testing                | Adding or correcting tests, with no changes to production code.                          |
| build                  | Changes to the build system or external dependencies.                                    |
| continuous-integration | Changes to CI configuration files and scripts.                                           |
| chore                  | Routine maintenance tasks that don't modify source or test files.                        |
| revert                 | Reverts a previous commit.                                                               |

## Building for Production

To create a standalone executable:

```bash
python3 -m cli build
```

This will build the Vue frontend, then use PyInstaller (via `cli.commands.build_pyinstaller`) to bundle the Python
backend and the built UI into a single executable located in the `dist/` folder.

## Troubleshooting

1. **Dependencies:** If you encounter issues, try running `python3 -m cli setup` again to ensure all tools (Bun, UV) and
   packages are correctly installed.
2. **Python Version:** Ensure `python --version` reports 3.13 or higher.
3. **Port Conflicts:** The dev server uses port `5173`. Ensure it is available.

## License

- **TODO:** Add license information (e.g., MIT, Apache 2.0).
