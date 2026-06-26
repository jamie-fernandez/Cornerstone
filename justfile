set shell := ["bash", "-c"]

# Default recipe: list all available commands
default:
    @just --list

# --- Core Workflows ---

# Initialize development environment (installs Bun, UV, and dependencies)
setup:
    python commands/setup.py

# Start application with hot-reloading
dev:
    bash commands/start-dev

# Alias for 'dev'
start: dev

# --- Quality Control ---

# Run all unit tests (backend and frontend)
test: test-app test-ui

# Run backend Python tests (Pytest)
test-app:
    uv run pytest app/__tests__/

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
    uv run ruff check --fix .

# --- Build ---

# Build the application for production
build:
    bash commands/build

# Alias for 'build' (platform specific commands can be added here later)
build-mac: build
build-win: build

# --- CI Helpers ---

# Run local GitLab CI jobs (requires gitlab-ci-local)
ci task="":
    gitlab-ci-local {{task}}

# Clean build artifacts
clean:
    rm -rf dist/
