# Agentic AI Developer Guide (AGENTS.md)

Welcome, AI Agent! This guide is designed to help you navigate, understand, and contribute to the **Cornerstone** project efficiently. Cornerstone is a cross-platform desktop application template using Vue.js for the frontend and Python for the backend.

The project is hosted on **GitLab**: [https://gitlab.com/jnf-desktop-apps/cornerstone](https://gitlab.com/jnf-desktop-apps/cornerstone)

## 🚀 Quick Tech Stack Reference

- **Frontend:** Vue 3, Vite, Vuetify 3, Tailwind CSS 4, Pinia.
- **Backend:** Python 3.13+, `pywebview`, SQLAlchemy (SQLite).
- **Tooling:** Bun (JS), UV (Python - **Preferred over pip**), Biome (Linting JS), Ruff (Linting Python), [just](https://github.com/casey/just) (Command runner), [gitlab-ci-local](https://github.com/firecow/gitlab-ci-local).
- **Testing:** Vitest (Frontend), Pytest (Backend), Cypress (E2E).

## 🏗️ Architecture: The Python-JS Bridge

Cornerstone uses `pywebview` to bridge the Python backend and the Vue frontend.

### How it works:
1.  **Exposure:** The `API` class in `app/api.py` is instantiated and passed to `webview.create_window(..., js_api=api)` in `start.py`.
2.  **Consumption:** The frontend never touches `window.pywebview.api` directly (it is injected asynchronously). All calls go through `callApi('method_name', ...args)` from `ui/utils/bridge.js`, which waits for the `pywebviewready` event, unwraps the response envelope, and throws `BridgeError` on error envelopes.
3.  **Asynchrony:** Calls from JS to Python are asynchronous and return a Promise (`callApi` resolves with the unwrapped `data` payload).
4.  **Response Envelope:** Data-returning API methods are decorated with `@bridge_method` and always return `{"status": "success", "data": ...}` or `{"status": "error", "message": ...}`.
5.  **Mock Fallback:** When pywebview is not injected (plain-browser `vite dev`, Cypress E2E runs), `callApi` falls back to the mock in `ui/utils/bridge.mock.js`. Keep the mock in sync with the `API` class.
6.  **Database Lifecycle:** `init_db()` is called explicitly in `start.py` (never at import time). Bridge methods use `get_session()` from `app/database.py` for session-per-call transactions with automatic commit/rollback.

## 🛠️ Core Workflows

### 1. Initialization
Always start by ensuring the environment is set up.
```bash
just setup
```
This command handles both `bun install` and `uv sync`.

### 2. Development
To start the application with hot-reloading:
```bash
just dev
```
Note: This requires both the Vite dev server and the Python process to be running.

### 3. Testing
- **Frontend:** `bun run test:ui:unit`
- **Backend:** `just test-app`
- **E2E:** `bun run test:ui:e2e`
- **CI Pipelines (Local):** Use [gitlab-ci-local](https://github.com/firecow/gitlab-ci-local) to run and debug GitLab CI jobs locally.
- **CI Pipelines (Remote):** The `.gitlab-ci.yml` defines stages for `setup` (Merge Request automation), `lint` (Ruff/Biome, `pip-audit`), `test` (Pytest/Vitest with JUnit + Cobertura reports, Cypress E2E, GitLab Secret-Detection/SAST templates), `build` (per-OS dry-run builds), `release` (version tags), and `renovate`. Behavior worth knowing:
  - Jobs cache deps keyed on `uv.lock`/`bun.lock`, install with `--locked`/`--frozen-lockfile`, and skip when a change doesn't touch their stack (`rules:changes`); `interruptible` cancels superseded pipelines. Scheduled pipelines run Renovate only.
  - The `cypress/included` image version must match `devDependencies.cypress` in `package.json` (Renovate groups them); its `entrypoint` must stay overridden to `[""]`, and `NODE_OPTIONS=--dns-result-order=ipv4first` is required for `vite preview`/`wait-on` to agree on loopback in containers.
  - Frontend coverage uses the Istanbul provider, not v8 — v8 needs Node's inspector APIs, but CI runs Vitest under the Bun runtime (the `oven/bun` image has no Node).
  - Pushing a version tag (e.g. `v0.2.0`) runs the release build and creates a GitLab Release with the Linux bundle attached.
  - Ensure `SETTINGS__GITLAB_ACCESS_TOKEN` is configured in GitLab CI/CD variables. **Important:** Uncheck the "Protected" flag for this variable if you want the automation to work on Merge Request pipelines from non-protected feature branches.

## ➕ How to Add a New Feature

To add a feature that requires backend logic:

1.  **Backend (Python):**
    -   Add a new method to the `API` class in `app/api.py`, decorated with `@bridge_method`.
    -   If data persistence is needed, define a model in `app/models.py` and run transactions with `get_session()` from `app/database.py`.
    -   Only return JSON-serializable data across the bridge; convert ORM objects with `model.to_dict()` (never return ORM instances).
    -   Raise `BridgeError` for user-facing error messages; unexpected exceptions are logged server-side and return a generic error to JS.
    -   Mirror the new method in `ui/utils/bridge.mock.js` so browser dev and E2E tests keep working.
2.  **Frontend (Vue):**
    -   Call the new method using `callApi('your_method_name')` from `ui/utils/bridge.js`.
    -   Example: `const stats = await callApi('get_system_stats')` inside `try...catch`; a caught `BridgeError` carries the user-facing Python message.
3.  **State Management:**
    -   Use Pinia stores in `ui/stores/` to manage the data if it needs to be shared across components.

## 📏 Coding Standards

- **Python:** Follow PEP 8. Use **Ruff** for linting.
- **JavaScript/Vue:** Use **Biome** for formatting and linting.
- **Communication:** Always use the `callApi` client (`ui/utils/bridge.js`) for backend communication; avoid direct HTTP calls unless interacting with external services.

## 📂 Key Files Map

- `start.py`: Application entry point and window configuration.
- `app/api.py`: The "Brain" - defines the interface between JS and Python.
- `app/decorators.py`: Bridge decorators (`@bridge_method` response envelope).
- `app/exceptions.py`: Bridge exception types (`BridgeError` for user-facing messages).
- `app/models.py`: Database schema definitions.
- `ui/utils/bridge.js`: Frontend bridge client (`callApi`, bridge-readiness wait, mock fallback).
- `ui/App.vue`: Root frontend component.
- `ui/pages/`: Main view components.
- `commands/`: Utility scripts for setup, build, and deployment.

## 📝 Documentation Updates

- **Keep it Synchronized:** When adding features or changing commands, always update `README.md` (for users) and `AGENTS.md` (for developers/agents).
- **Self-Documenting Code:** Use clear function names and Docstrings in Python, and JSDoc in Vue components.

## 🏷️ GitLab Labels

| Label | Description |
|---|---|
| frontend | Changes related to the Vue.js frontend (ui/ directory). |
| backend | Changes related to the Python backend (app/ directory or start.py file). |
| feature | A new feature for the user; aligns with a MINOR version bump in semver. |
| fix | A bug fix for the user; aligns with a PATCH version bump in semver. |
| breaking-change | A change that breaks backward compatibility; aligns with a MAJOR version bump in semver. |
| documentation | Changes to documentation only, with no effect on code behavior. |
| style | Formatting or whitespace changes that don't affect code logic. |
| refactor | A code change that neither fixes a bug nor adds a feature. |
| performance | A code change that improves performance. |
| testing | Adding or correcting tests, with no changes to production code. |
| build | Changes to the build system or external dependencies. |
| continuous-integration | Changes to CI configuration files and scripts. |
| chore | Routine maintenance tasks that don't modify source or test files. |
| revert | Reverts a previous commit. |

## 🔒 Security

- **Input Validation:** Always treat data coming from the JS bridge as untrusted. Validate types and values in Python.
- **Secrets Management:** Never hardcode API keys or credentials. Use environment variables or a secure configuration loader (planned).
- **JS Bridge Exposure:** Only expose necessary methods in the `API` class. Avoid exposing sensitive system-level functions directly.

## 🛠️ Refactoring Best Practices

- **Consistency:** Follow the established patterns. If a feature uses Pinia for state, don't introduce a different state management library without a strong reason.
- **Dry Principle:** Extract shared logic into utility files in `ui/utils/` or `app/utils/`.
- **Linting:** Always run `bun run lint:fix` before submitting changes to ensure both Python (Ruff) and JS (Biome) code meets project standards.

## 🌿 Using Git (Context Gathering)

Use these commands to gather context efficiently:

### Working Branch Context
* `git branch --show-current` -> Outputs only the active branch name.
* `git status -sb` -> Highly condensed, short-format status with branch tracking information.
* `git diff --stat` -> High-density list of changed files and lines without printing full code diffs.
* `git log --pretty=format:"%h - %s (%cr) [%an]"` --abbrev-commit -30 -> Compact, single-line log showing hash, title, age, and author for the last 30 commits.

### Remote Branch Context (Target: main)
Use these commands for critical changes destined for production (`origin/main`):
* `git log origin/main..HEAD --pretty=format:"%h %s"` -> Raw, ultra-short list of commit titles missing from production.
* `git diff origin/main...HEAD --stat` -> High-level summary of total production alterations introduced by this branch.
* `git diff origin/main...HEAD -w --minimal` -> Token-efficient line-by-line code changes while ignoring whitespace changes and layout formatting noise.

## ✅ Definition of Done

Before submitting your changes, ensure:

- **All Tests Pass:** Frontend unit, backend unit, and E2E tests are successful.
- **New Code Includes Tests:** All new logic and bug fixes are covered by tests.
- **Linting & Formatting:** `bun run lint:fix` and `ruff check --fix .` has been run and passes.
- **Documentation Updated:** `README.md` and `AGENTS.md` are synchronized with changes.
- **Security:** Input validation is applied to all data received via the JS bridge.
- **Consistency:** The implementation follows established coding standards and patterns.

## 🤖 Tips for AI Agents

- **Environment Detection:** Use `getattr(sys, 'frozen', False)` in Python to check if the app is running as a packaged executable.
- **Error Handling:** Bridge methods return a `{"status", ...}` envelope, which `callApi` unwraps. Wrap `callApi` calls in `try...catch`: `BridgeError` carries the user-facing Python message; `BridgeUnavailableError` means the bridge or method is missing.
- **Logging:** Use the logger defined in `app/database.py` for backend logs.
- **Dependency Management:** Use `uv add <package>` for Python (instead of `pip install`) and `bun add <package>` for JS. Do not manually edit `pyproject.toml` or `package.json` unless necessary. Ensure `uv.lock` and `bun.lock` are committed.

<!-- CODEGRAPH_START -->
## CodeGraph

In repositories indexed by CodeGraph (a `.codegraph/` directory exists at the repo root), reach for it BEFORE grep/find or reading files when you need to understand or locate code:

- **MCP tool** (when available): `codegraph_explore` answers most code questions in one call — the relevant symbols' verbatim source plus the call paths between them, including dynamic-dispatch hops grep can't follow. Name a file or symbol in the query to read its current line-numbered source. If it's listed but deferred, load it by name via tool search.
- **Shell** (always works): `codegraph explore "<symbol names or question>"` prints the same output.

If there is no `.codegraph/` directory, skip CodeGraph entirely — indexing is the user's decision.
<!-- CODEGRAPH_END -->

<!-- context7 -->
Use the `ctx7` CLI to fetch current documentation whenever the user asks about a library, framework, SDK, API, CLI tool, or cloud service — even well-known ones like React, Next.js, Prisma, Express, Tailwind, Django, or Spring Boot. This includes API syntax, configuration, version migration, library-specific debugging, setup instructions, and CLI tool usage. Use even when you think you know the answer — your training data may not reflect recent changes. Prefer this over web search for library docs.

Do not use for: refactoring, writing scripts from scratch, debugging business logic, code review, or general programming concepts.

## Steps

1. Resolve library: `bunx ctx7@latest library <name> "<what to look up>"` — use the official library name with proper punctuation (e.g., "Next.js" not "nextjs", "Customer.io" not "customerio", "Three.js" not "threejs")
2. Pick the best match (ID format: `/org/project`) by: exact name match, description relevance, code snippet count, source reputation (High/Medium preferred), and benchmark score (higher is better). If results don't look right, try alternate names or queries (e.g., "next.js" not "nextjs", or rephrase the question)
3. Fetch docs: `bunx ctx7@latest docs <libraryId> "<what to look up>"` — run a separate `docs` command per distinct concept if the question spans multiple topics, unless it's about how they interact
4. Answer using the fetched documentation

You MUST call `library` first to get a valid ID unless the user provides one directly in `/org/project` format. Be specific about what to look up in the library's documentation — specific and detailed queries return better results than vague single words, but keep each query to a single concept unless the question is about how concepts interact; combined multi-topic queries dilute ranking and return shallow results for each topic. Do not run more than 3 commands per question. Do not include sensitive information (API keys, passwords, credentials) in queries.

For version-specific docs, use `/org/project/version` from the `library` output (e.g., `/vercel/next.js/v14.3.0`).

If a command fails with a quota error, inform the user and suggest `bunx ctx7@latest login` or setting `CONTEXT7_API_KEY` env var for higher limits. Do not silently fall back to training data.
<!-- context7 -->
