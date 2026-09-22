# CLI Reference & Developer Tools

Cornerstone provides a built-in Typer CLI (`stone` / `cornerstone`) with rich formatting, code generators, environment diagnostics, and database management utilities.

---

## 💻 Invocation Methods

You can invoke the CLI through several flexible methods:

- **Direct Shorthand:** `stone <command>`
- **Via UV:** `uv run cornerstone <command>`
- **Via Just:** `just cli <command>`
- **Interactive Docs:** `stone docs` or `stone docs <command>`

---

## 🛠️ Commands Catalog

### General & Diagnostics

| Command        | Purpose                                                  | Example         |
|:---------------|:---------------------------------------------------------|:----------------|
| `stone --help` | View all CLI commands and available options.             | `stone --help`  |
| `stone doctor` | Run environment, dependency, and GUI driver diagnostics. | `stone doctor`  |
| `stone info`   | Display application details and runtime configuration.   | `stone info`    |
| `stone stats`  | Display system metrics, memory, and resource usage.      | `stone stats`   |
| `stone clean`  | Clean up build artifacts (`dist`, `build`, `*.spec`).    | `stone clean`   |
| `stone docs`   | Browse interactive CLI documentation in the terminal.    | `stone docs db` |

### Code Generators (`stone make`)

| Generator                 | Purpose                                              | Example                      |
|:--------------------------|:-----------------------------------------------------|:-----------------------------|
| `stone make api <name>`   | Scaffold a new bridge API method with frontend mock. | `stone make api get_metrics` |
| `stone make page <name>`  | Scaffold a new Vue page component and route.         | `stone make page Settings`   |
| `stone make model <name>` | Scaffold an SQLAlchemy database model.               | `stone make model Project`   |

### Git Hooks

| Command               | Purpose                                          | Example               |
|:----------------------|:-------------------------------------------------|:----------------------|
| `stone hooks install` | Install Git pre-commit hooks for Ruff and Biome. | `stone hooks install` |

### Database & Migrations (`stone db`)

| Command                       | Purpose                                         | Example                                    |
|:------------------------------|:------------------------------------------------|:-------------------------------------------|
| `stone db info`               | Inspect SQLite database path, size, and tables. | `stone db info`                            |
| `stone db test`               | Test SQLite connectivity.                       | `stone db test`                            |
| `stone db init`               | Initialize schema and run migrations to head.   | `stone db init`                            |
| `stone db migrate -m "<msg>"` | Generate a new sequential migration revision.   | `stone db migrate -m "create_users_table"` |
| `stone db upgrade`            | Apply pending migrations to head.               | `stone db upgrade`                         |
| `stone db downgrade`          | Revert previous migration revision.             | `stone db downgrade`                       |
| `stone db current`            | Inspect current migration revision.             | `stone db current`                         |
| `stone db history`            | View chronological migration history.           | `stone db history`                         |
| `stone db tables`             | List database schema and column details.        | `stone db tables`                          |
| `stone db query "<sql>"`      | Execute raw SQL query (supports `--json`).      | `stone db query "SELECT * FROM users"`     |
| `stone db reset --yes`        | Reset and re-create database file.              | `stone db reset --yes`                     |
