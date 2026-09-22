# Getting Started

This guide walks you through setting up your environment, installing dependencies, and launching Cornerstone in development mode.

---

## 📋 Prerequisites

Before getting started, make sure you have the following installed:

- **Python:** Version 3.13 or higher.
- **Bun:** (Fast JavaScript package manager and runtime) — auto-installed during `stone setup` if missing.
- **UV:** (High-performance Python package manager) — auto-installed during `stone setup` if missing.
- **Just (Optional but recommended):** Command runner for simplified terminal workflows.

---

## 🚀 1. Setup Development Environment

Run the automated setup command to install tools, configure the Python virtual environment (`.venv`), and install all frontend and backend dependencies:

```bash
stone setup
# or with just:
just setup
```

### What this does:
1. **Tooling Verification:** Checks for `bun` and `uv`, offering automated installation if they are not detected.
2. **Frontend Dependencies:** Installs node modules using `bun install`.
3. **Backend Dependencies:** Resolves Python packages and synchronizes the virtual environment using `uv sync`.

---

## 💻 2. Start the Development Server

To start the application with hot-reloading for both the Vue frontend and the Python backend:

```bash
stone dev
# or with just:
just dev
```

### What to expect:
1. The **Vite** development server starts and serves the Vue frontend at `http://localhost:5173`.
2. The **Python** backend process starts and opens a native desktop window powered by `pywebview`.
3. Any edits made to Vue components or Python files reload automatically.

---

## ⚡ Using Just Commands

If you have [just](https://github.com/casey/just) installed, you can take advantage of these handy shortcuts:

```bash
just setup       # Initialize environment and install dependencies
just doctor      # Run health diagnostics on dependencies and system drivers
just dev         # Start development mode with hot-reloading
just test        # Run backend and frontend test suites
just lint        # Run code linters (Ruff + Biome)
just lint-fix    # Run linters and auto-apply formatting fixes
just build       # Package standalone desktop executable
```

---

## 🔍 System Health Check

If you encounter issues during startup or want to verify your GUI drivers:

```bash
stone doctor
# or
just doctor
```

This runs diagnostics on:
- Python version and UV installation
- Node.js / Bun runtime versions
- Platform-specific GUI webview backends (WebKitGTK on Linux, WebKit on macOS, WebView2 on Windows)
- Database connectivity and migration state
