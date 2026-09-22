# Architecture & The Bridge

Cornerstone provides a robust, decoupled desktop application architecture combining a modern Vue.js single-page frontend with a Python backend, unified through `pywebview`.

---

## 🏗️ The Python-JS Bridge

```
┌────────────────────────────────────────┐
│           Vue.js 3 Frontend            │
│   (Pinia Stores, Vuetify, Tailwind)    │
└───────────────────┬────────────────────┘
                    │ callApi('method_name', ...args)
                    │ returns Promise (unwrapped data payload)
                    ▼
┌────────────────────────────────────────┐
│            Bridge Client               │
│          (ui/utils/bridge.js)          │
│   • Waits for pywebviewready event     │
│   • Unwraps {"status", "data"} envelope│
│   • Throws BridgeError on failure      │
│   • Falls back to mock in dev/e2e      │
└───────────────────┬────────────────────┘
                    │ window.pywebview.api.method_name(...)
                    ▼
┌────────────────────────────────────────┐
│        Python pywebview Bridge         │
│             (app/api.py)               │
│   • Decorated with @bridge_method      │
│   • Session-per-call get_session()     │
│   • Returns JSON-serializable dicts    │
└───────────────────┬────────────────────┘
                    │ ORM & Data Layer
                    ▼
┌────────────────────────────────────────┐
│       SQLAlchemy / SQLite Database     │
│      (app/models.py, migrations/)      │
└────────────────────────────────────────┘
```

### 1. Exposure
The `API` class in `app/api.py` exposes backend methods to JavaScript. When `start.py` launches `pywebview`, it attaches an instance of this class:
```python
api = API()
webview.create_window(..., js_api=api)
```

### 2. Method Decoration & Response Envelope
All API methods intended for bridge consumption are decorated with `@bridge_method` (defined in `app/decorators.py`). The decorator standardizes return values into a structured envelope:
- **Success:** `{"status": "success", "data": ...}`
- **User Error (`BridgeError`):** `{"status": "error", "message": "User-facing message"}`
- **Unhandled Exception:** `{"status": "error", "message": "An internal error occurred."}` (logs traceback server-side)

### 3. Consumption from Vue
Frontend components never call `window.pywebview.api` directly. Instead, they use `callApi` from `ui/utils/bridge.js`:

```javascript
import { callApi } from '@/utils/bridge.js';

try {
  const stats = await callApi('get_system_stats');
  console.log('System stats:', stats);
} catch (error) {
  console.error('API Error:', error.message);
}
```

`callApi` handles:
- Waiting asynchronously for the `pywebviewready` event before executing.
- Unwrapping the data payload from the response envelope.
- Throwing a `BridgeError` when the backend returns an error envelope.
- Seamless fallback to `ui/utils/bridge.mock.js` when running in standalone browser mode (`bun run dev`) or Cypress E2E test runs.

---

## 🗂️ Project Structure

```text
cornerstone/
├── alembic.ini              # Alembic database migration configuration
├── app/                     # Python Backend
│   ├── api.py               # JS-exposed bridge API methods
│   ├── config.py            # Centralized application configuration
│   ├── database.py          # SQLAlchemy engine, session maker, init_db()
│   ├── decorators.py        # Bridge decorators (@bridge_method)
│   ├── exceptions.py        # Exception classes (BridgeError)
│   ├── migrations/          # Alembic migration scripts and versions
│   ├── models.py            # SQLAlchemy database models
│   └── __tests__/           # Backend unit tests (pytest)
├── cli/                     # Typer CLI & Developer Automation
│   ├── commands/            # CLI subcommands (build, clean, db, dev, doctor, init, make, setup)
│   ├── common.py            # Executable finders and project utilities
│   ├── main.py              # Typer CLI entrypoint
│   └── __tests__/           # CLI unit tests (pytest)
├── docs/                    # Cornerstone Documentation
│   ├── README.md            # Documentation table of contents
│   ├── getting-started.md   # Setup and first run
│   ├── architecture.md      # Architecture and bridge deep-dive
│   ├── rebranding.md        # Customization & fork rebranding
│   ├── cli.md               # CLI command reference
│   ├── database.md          # Models and migrations guide
│   ├── development.md       # Testing and CI/CD guide
│   └── building.md          # Production packaging
├── ui/                      # Vue.js 3 Frontend
│   ├── App.vue              # Root Vue component
│   ├── main.js              # Vite frontend entrypoint
│   ├── pages/               # Vue views and page components
│   ├── stores/              # Pinia state stores
│   ├── utils/               # Bridge client & mock fallback
│   └── __tests__/           # Frontend unit tests (Vitest)
├── cypress/                 # Cypress E2E test suite
├── pyproject.toml           # Python configuration, dependencies, and CLI entry points
├── package.json             # Frontend dependencies and npm scripts
└── start.py                 # Desktop application window launcher
```
