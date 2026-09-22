# Cornerstone Documentation

Welcome to the Cornerstone documentation! Cornerstone is a robust cross-platform desktop application template that combines a modern Vue 3 frontend with a Python backend via `pywebview`.

This documentation directory contains in-depth guides for setting up, developing, extending, testing, and packaging your desktop application.

---

## 📚 Table of Contents

| Guide                                               | Description                                                                                       |
|:----------------------------------------------------|:--------------------------------------------------------------------------------------------------|
| 🚀 **[Getting Started](getting-started.md)**        | Prerequisites, environment setup (`stone setup`), and running in development mode (`stone dev`).  |
| 🏗️ **[Architecture & The Bridge](architecture.md)** | Understand how the Python backend and Vue.js frontend communicate asynchronously via `pywebview`. |
| 🎨 **[Rebranding & Customization](rebranding.md)**  | Transform the template into your own customized desktop application using `stone init`.           |
| 🛠️ **[CLI Reference](cli.md)**                      | Complete reference for the built-in Typer CLI commands, code generators, and utilities.           |
| 🗄️ **[Database & Migrations](database.md)**         | Working with SQLite, SQLAlchemy models, and sequential Alembic database migrations.               |
| 🧪 **[Development & Testing](development.md)**      | Unit testing (Vitest, Pytest), E2E testing (Cypress), CI/CD pipelines, and linting.               |
| 📦 **[Building & Distribution](building.md)**       | Packaging standalone desktop executables for macOS, Windows, and Linux via PyInstaller.           |

---

## 🤖 AI Agent Guidelines

If you are developing with AI coding assistants (e.g. JetBrains Junie, Claude, Cursor), refer to **[AGENTS.md](../AGENTS.md)** in the project root for agentic development standards, tool workflows, and coding rules.

---

## 💡 Quick Links

- **Upstream Repository:** [https://gitlab.com/jnf-desktop-apps/cornerstone](https://gitlab.com/jnf-desktop-apps/cornerstone)
- **Frontend Framework:** [Vue.js 3](https://vuejs.org/) • [Vuetify 3](https://vuetifyjs.com/) • [Tailwind CSS 4](https://tailwindcss.com/)
- **Backend Framework:** [Python 3.13+](https://www.python.org/) • [pywebview](https://pywebview.flowrl.com/) • [SQLAlchemy](https://www.sqlalchemy.org/)
- **Package Managers:** [Bun](https://bun.sh/) • [UV](https://docs.astral.sh/uv/)
