import os
import shutil
import subprocess
import sys


def build_app():
    print("Starting PyInstaller build...")

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Make the app package importable so the build name follows the same
    # single source of truth as the running app (pyproject.toml -> CONFIG).
    sys.path.insert(0, project_root)
    from app.config import CONFIG

    UI_dist_dir = os.path.join(project_root, "ui", "dist")
    app_path = os.path.join(project_root, "start.py")
    pyproject_path = os.path.join(project_root, "pyproject.toml")

    dist_dir = os.path.join(project_root, "dist")
    build_dir = os.path.join(project_root, "build")

    # Verify UI dist directory exists
    if not os.path.exists(UI_dist_dir):
        print(f"ERROR: UI dist directory not found at {UI_dist_dir}")
        print("Please run 'bun run vite build' first to build the Vue app.")
        return

    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)

    # Determine the correct path separator for --add-data based on OS
    separator = ";" if os.name == "nt" else ":"

    args = [
        "pyinstaller",
        "--windowed",
        "--clean",
        "--add-data",
        f"{UI_dist_dir}{separator}ui/dist",
        # Bundle pyproject.toml so the frozen app can read its own identity.
        "--add-data",
        f"{pyproject_path}{separator}.",
        "--name",
        CONFIG["NAME"],
        app_path,
    ]

    subprocess.run(args, check=True)

    print(f"PyInstaller build complete: {CONFIG['NAME']}")


if __name__ == "__main__":
    build_app()
