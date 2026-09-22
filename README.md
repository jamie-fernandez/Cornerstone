# Cornerstone

> A modern, batteries-included template repository for building cross-platform desktop applications using Vue.js 3 and Python 3.13+, bridged seamlessly via `pywebview`.

---

## 🚀 Quick Start

```bash
# 1. Install dependencies and set up virtual environments
stone setup   # or `just setup`

# 2. Run the application in development mode with hot-reload
stone dev     # or `just dev`

# 3. Rebrand the template into your own application in one step
stone init "My App" -d "A powerful desktop application."
```

---

## ⚡ Tech Stack

- **Frontend:** [Vue.js 3](https://vuejs.org/) • [Vite](https://vitejs.dev/) • [Vuetify 3](https://vuetifyjs.com/) • [Tailwind CSS 4](https://tailwindcss.com/) • [Pinia](https://pinia.vuejs.org/)
- **Backend:** [Python 3.13+](https://www.python.org/) • [pywebview](https://pywebview.flowrl.com/) • [SQLAlchemy](https://www.sqlalchemy.org/) • [Alembic](https://alembic.sqlalchemy.org/)
- **Tooling:** [Bun](https://bun.sh/) • [UV](https://docs.astral.sh/uv/) • [Biome](https://biomejs.dev/) • [Ruff](https://docs.astral.sh/ruff/) • [just](https://github.com/casey/just)
- **Testing:** [Vitest](https://vitest.dev/) • [Pytest](https://pytest.org/) • [Cypress](https://www.cypress.io/)

---

## 📖 Documentation

Comprehensive documentation, architectural deep dives, CLI guides, and development workflows are organized in the **[`docs/`](docs/)** directory:

- 📚 **[Documentation Overview & Table of Contents](docs/README.md)**
- 🚀 **[Getting Started Guide](docs/getting-started.md)** — Prerequisites, environment setup, and development workflow.
- 🏗️ **[Architecture & The Bridge](docs/architecture.md)** — Python-JS bridge mechanism, request lifecycle, and project structure.
- 🎨 **[Rebranding & Customization](docs/rebranding.md)** — Rebranding wizard, clean examples, and making the template your own.
- 🛠️ **[CLI Reference](docs/cli.md)** — Built-in `stone` commands, code generators, and utilities.
- 🗄️ **[Database & Migrations](docs/database.md)** — Working with SQLite models and sequential Alembic migrations.
- 🧪 **[Development & Testing](docs/development.md)** — Unit tests, E2E testing with Cypress, and CI/CD pipelines.
- 📦 **[Building & Distribution](docs/building.md)** — Packaging standalone executables for macOS, Windows, and Linux.

---

## 🤖 For AI Developers & Agents

If you are developing with an AI coding assistant, refer to **[AGENTS.md](AGENTS.md)** for developer instructions, architecture conventions, and coding standards.
