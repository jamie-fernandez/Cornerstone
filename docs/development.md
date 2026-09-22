# Development & Testing Workflows

Cornerstone comes equipped with testing harnesses across all layers of the application stack, automated pre-commit quality checks, and multi-platform CI/CD pipelines.

---

## 🧪 Testing

### Frontend Unit Tests (Vitest)
Unit tests for Vue components and bridge utilities reside in `ui/__tests__/`.

```bash
bun run test:ui:unit
```

### Backend Unit Tests (Pytest)
Python backend and bridge tests reside in `app/__tests__/`. CLI tests reside in `cli/__tests__/`.

```bash
# Run all backend and CLI tests
just test

# Run only backend tests
just test-app

# Run only CLI tests
just test-cli
```

### End-to-End Tests (Cypress)
Cypress E2E specs reside in `cypress/e2e/`.

```bash
bun run test:ui:e2e
```

---

## 🧹 Code Quality & Linting

- **Python:** Linted with [Ruff](https://docs.astral.sh/ruff/).
- **JavaScript & Vue:** Formatted and linted with [Biome](https://biomejs.dev/).

```bash
# Check formatting and linting
just lint

# Automatically apply formatting fixes
just lint-fix
# or
bun run lint:fix
```

### Pre-Commit Hooks

Install automated Git pre-commit hooks to verify staged files prior to committing:

```bash
stone hooks install
# or
just setup-hooks
```

---

## 🚀 CI/CD Pipelines

Cornerstone includes ready-to-use continuous integration workflows for both GitHub Actions and GitLab CI.

### GitHub Actions (`.github/workflows/ci.yml`)
- Multi-OS test matrix across Ubuntu, macOS, and Windows.
- Python 3.13 and 3.14 coverage.
- Linter checks (Ruff & Biome).
- Pytest backend tests, Vitest unit tests, and Cypress E2E.
- Dry-run PyInstaller builds on all three operating systems.

### GitLab CI (`.gitlab-ci.yml`)
- Stages: `setup`, `lint`, `test`, `build`, `release`.
- Code coverage reporting (JUnit and Cobertura formats) integrated directly into GitLab Merge Requests.
- Security scanning via GitLab Secret-Detection and SAST templates.
- Local execution and debugging using [gitlab-ci-local](https://github.com/firecow/gitlab-ci-local).

---

## 🏷️ GitLab Merge Request Labels

| Label             | Description                                       | Semver Impact |
|:------------------|:--------------------------------------------------|:--------------|
| `frontend`        | Changes to Vue components or UI assets (`ui/`).   | —             |
| `backend`         | Changes to Python logic, API, or models (`app/`). | —             |
| `feature`         | New user-facing capability.                       | MINOR bump    |
| `fix`             | Bug fix.                                          | PATCH bump    |
| `breaking-change` | Incompatible API or structural modification.      | MAJOR bump    |
| `documentation`   | Updates to docs and markdown files.               | —             |
| `refactor`        | Code restructuring without behavior change.       | —             |
| `performance`     | Performance optimization.                         | —             |
| `testing`         | Test additions or corrections.                    | —             |
| `build` / `chore` | Build scripts, dependencies, or maintenance.      | —             |
