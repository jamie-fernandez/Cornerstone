# Cornerstone

A desktop app template built with Vue.js, Vite, and Python.

## About This Template

Cornerstone is a starter template for building cross-platform desktop applications using:
- **Frontend:** Vue.js 3 with Vite for fast development
- **Backend:** Python with a REST API
- **Package Managers:** Bun for Node.js, UV for Python
- **Testing:** Vitest for frontend, Pytest for backend, Cypress for E2E

## Prerequisites

- **Node.js** (latest LTS recommended)
- **Python** 3.8+
- **Bun.js** (will be auto-installed if missing)
- **UV** (will be auto-installed if missing)

## Getting Started

### 1. Setup Development Environment

Run the setup command to install all dependencies:

```bash
bun run setup
```

**What to expect:**
- ✓ Checks for Bun.js and installs it if needed
- ✓ Checks for UV (Python package manager) and installs it if needed
- ✓ Installs Node.js dependencies using Bun
- ✓ Installs Python dependencies using UV
- Clear console messages showing each step of the process

### 2. Start the Application

Once setup is complete, start the development server:

```bash
bun run start
```

**What to expect:**
- ✓ Launches the Vue.js frontend development server
- ✓ Starts the Python backend API server
- ✓ Both servers run concurrently with hot-reload enabled
- ✓ Application will be available in your browser (typically http://localhost:5173)

## Project Structure

```
cornerstone/
├── app/                    # Python backend
│   ├── api.py             # API routes
│   ├── models.py          # Database models
│   ├── database.py        # Database configuration
│   └── __tests__/         # Python unit tests
├── ui/                    # Vue.js frontend
│   ├── App.vue            # Main component
│   ├── router.js          # Route configuration
│   ├── main.js            # Entry point
│   ├── pages/             # Page components
│   ├── stores/            # Pinia state management
│   └── __tests__/         # Frontend tests
├── cypress/               # End-to-end tests
└── commands/              # Setup and build scripts
```

## Available Commands

| Command                | Purpose                            |
| ---------------------- | ---------------------------------- |
| `bun run setup`        | Initialize development environment |
| `bun run start`        | Start development servers          |
| `bun run test:ui:unit` | Run all frontend unit tests        |
| `bun run test:app`     | Run python unit tests              |

## Development Notes

- The setup script handles virtual environment management via UV
- Both frontend and backend servers support hot-reload during development
- Tests can be run independently for frontend (vitest) and backend (pytest)

## Troubleshooting

If you encounter issues during setup:
1. Ensure you have Node.js and Python installed
2. Run `bun run setup` again to reinstall dependencies
3. Check that Bun and UV installed successfully
