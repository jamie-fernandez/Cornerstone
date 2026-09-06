set shell := ["bash", "-c"]

# Dynamically resolve the primary CLI script name from pyproject.toml
cli := `uv run tomlq -r '.project.scripts | keys[0]' pyproject.toml`

# Default recipe: list all available commands
default:
    @just --list

# --- Core Workflows ---

# Rebrand this template into your own app (e.g. just init "My App" [--clean-examples])
init *name:
    {{cli}} init {{name}}

# Initialize development environment (installs Bun, UV, and dependencies)
setup:
    {{cli}} setup

# Run environment and dependency diagnostics
doctor:
    {{cli}} doctor

# Install git pre-commit hooks (Ruff and Biome on staged files)
setup-hooks:
    {{cli}} hooks install

# Start application with hot-reloading
dev:
    {{cli}} dev

# Alias for 'dev'
start: dev

# Run the application CLI (e.g. just cli --help, just cli db info)
cli *args:
    uv run python -m cli {{args}}

# --- Quality Control ---

# Run all unit tests (backend, cli, and frontend)
test: test-app test-cli test-ui

# Run backend Python tests (Pytest)
test-app:
    uv run pytest app/__tests__/

# Run CLI tests (Pytest)
test-cli:
    uv run pytest cli/__tests__/

# Run frontend Vue unit tests (Vitest)
test-ui:
    bun run test:ui:unit

# Run end-to-end tests (Cypress)
test-e2e:
    bun run test:ui:e2e

# Run end-to-end tests in interactive mode (Cypress Open)
test-e2e-dev:
    bun run test:ui:e2e:dev

# Run all linters (Biome for JS/Vue, Ruff for Python)
lint:
    bun x biome check .
    uv run ruff check .

# Run all linters and apply automatic fixes
lint-fix:
    bun run lint:fix
    uv run ruff check --fix .; uv run ruff format .

# --- Build ---

# Build the application for production
build:
    {{cli}} build

# Alias for 'build' (platform specific commands can be added here later)
build-mac: build
build-win: build

# --- CI Helpers ---

# Run local GitLab CI jobs (requires gitlab-ci-local)
ci task="":
    gitlab-ci-local {{task}}

# Clean build artifacts
clean:
    {{cli}} clean
