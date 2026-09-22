# Building & Distribution

Cornerstone packages your frontend and Python backend into a single standalone desktop executable using [PyInstaller](https://pyinstaller.org/).

---

## 📦 Creating a Production Build

To build the Vue frontend assets and package the desktop executable:

```bash
stone build
# or with just:
just build
```

### What the build process does:
1. **Frontend Compilation:** Runs `bun run build` to bundle Vue components, styles, and assets into `dist/`.
2. **PyInstaller Packaging:** Bundles the Python runtime, backend code, SQLite libraries, and UI assets into a standalone binary in the `dist/` directory.

---

## 🖥️ Platform-Specific Builds

```bash
# Package for macOS (.app / binary)
just build-mac

# Package for Windows (.exe)
just build-win

# Clean build artifacts
stone clean
# or
just clean
```

---

## ⚙️ How Application Metadata Works

Application metadata is configured in `pyproject.toml` under `[tool.app]`:

```toml
[project]
name = "cornerstone"
version = "0.1.0"

[tool.app]
display-name = "Cornerstone"
```

PyInstaller and `start.py` derive the window title, executable name, and bundle identifier dynamically from this single source of truth.
