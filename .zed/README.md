# Zed Editor Configuration

This directory contains the project-specific configuration for the Zed editor, tailored to the Cornerstone desktop application project.

## Configuration Overview

This project uses a mixed Python/JavaScript(Vue.js) stack with the following key technologies:
- Python backend with Bottle and PyWebview
- Vue.js frontend with Vite, TailwindCSS, and Vuetify
- Biome for JavaScript/TypeScript formatting and linting
- Ruff for Python formatting and linting

## Key Features Configured

### Languages & Formatting
- **Python**: Uses Ruff for formatting and linting (with Pyright disabled)
- **JavaScript/TypeScript/Vue**: Uses Biome for formatting, linting, and import organization (with TypeScript/ESLint servers disabled for redundancy)
- **JSON/HTML**: Uses appropriate language servers for formatting

### Editor Settings
- Vim mode enabled for efficient navigation
- Soft wrap enabled
- Trailing whitespace removal on save
- Final newline enforcement
- Catppuccin Macchiato theme for a pleasant visual experience

### Extensions Equivalents
From the original VS Code setup:
- `ms-python.python` & `ms-python.vscode-pylance` → Python language server via Ruff (with `!pyright` to avoid conflicts)
- `charliermarsh.ruff` → Ruff integration for Python formatting
- Biome handles the equivalent functionality of ESLint + Prettier for JS/TS

Note: For the Catppuccin theme and JetBrains Mono font, you may need to install the corresponding extensions in Zed:
1. `zed:catppuccin` for the theme
2. JetBrains Mono font should be installed separately on your system

## Updated Configuration Notes
- Corrected Zed settings structure based on current documentation
- `format_on_save` now uses simple "on"/"off" values rather than complex objects
- `language_servers` array uses "!" prefix to disable default servers that conflict with preferred ones
- Ruff and Biome are configured to work according to Zed's current language server integration
