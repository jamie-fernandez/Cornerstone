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
- **Package Managers:** [Bun](https://bun.sh/) & [UV](https://docs.astral.sh/uv/) (Python)
- **Code Quality:** [Biome](https://biomejs.dev/) (JS/TS) & [Ruff](https://docs.astral.sh/ruff/) (Python)
- **Testing:** [Vitest](https://vitest.dev/) (Unit), [Pytest](https://pytest.org/) (Backend), [Cypress](https://www.cypress.io/) (E2E)

## Requirements

- **Python:** 3.13 or higher
- **Bun:** (Will be auto-installed by setup if missing)
- **UV:** (Will be auto-installed by setup if missing)

## Getting Started

### 1. Setup Development Environment

Run the following command to install all dependencies and configure virtual environments:

```bash
python3 commands/setup.py
```

**What this does:**
- Checks for and installs **Bun.js** and **UV** if they are missing.
- Installs frontend dependencies using `bun install`.
- Installs Python dependencies and creates a virtual environment using `uv sync`.

### 2. Start the Application

To launch the application in development mode with hot-reload enabled for both frontend and backend:

```bash
bash commands/start-dev
```

**What to expect:**
- The Vite development server starts for the Vue frontend.
- The Python backend launches and opens a `pywebview` window.
- The application window will appear, loading the frontend from the dev server.

## Available Commands

| Command | Purpose |
| :--- | :--- |
| `python3 commands/setup.py` | Initialize the development environment and dependencies. |
| `bash commands/start-dev.sh` | Start both frontend and backend in development mode. |
| `bash commands/build.sh` | Build the production assets for both frontend and backend. |
| `bun run dev` | Start only the Vite development server (frontend). |
| `bun run test:ui:unit` | Run frontend unit tests using Vitest. |
| `bun run test:app` | Run backend unit tests using Pytest. |
| `bun run test:ui:e2e` | Run end-to-end tests using Cypress. |
| `bun run lint:fix` | Run Biome to check and fix code formatting/linting. |
| `bun run build:win` | Package the application as a Windows executable. |
| `bun run build:mac` | Package the application as a macOS bundle. |

## Project Structure

```text
cornerstone/
├── app/                # Python Backend
│   ├── api.py          # JS-exposed API classes
│   ├── config.py       # Backend configuration
│   ├── database.py     # Database & SQLAlchemy setup
│   ├── models.py       # Database models
│   └── __tests__/      # Backend unit tests
├── ui/                 # Vue.js Frontend
│   ├── App.vue         # Root Vue component
│   ├── main.js         # Frontend entry point
│   ├── pages/          # Vue page components
│   ├── stores/         # Pinia state management
│   └── __tests__/      # Frontend unit tests
├── commands/           # Development & Build scripts
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
bun run test:app
```

### End-to-End Tests
```bash
bun run test:ui:e2e
```

### GitLab CI (Local)
To test and debug GitLab CI pipelines locally, it is recommended to use [gitlab-ci-local](https://github.com/firecow/gitlab-ci-local).

## Building for Production

To create a standalone executable:

```bash
bash commands/build
```

This will build the Vue frontend, then use PyInstaller (via `commands/build-pyinstaller.py`) to bundle the Python backend and the built UI into a single executable located in the `dist/` folder.

## Troubleshooting

1. **Dependencies:** If you encounter issues, try running `python3 commands/setup.py` again to ensure all tools (Bun, UV) and packages are correctly installed.
2. **Python Version:** Ensure `python3 --version` reports 3.13 or higher.
3. **Port Conflicts:** The dev server uses port `5173`. Ensure it is available.

## License

- **TODO:** Add license information (e.g., MIT, Apache 2.0).
