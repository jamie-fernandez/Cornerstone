import subprocess
import os
import shutil


def build_app():
    print("Starting PyInstaller build...")

    project_root = os.path.dirname(os.path.dirname(__file__))
    UI_dist_dir = os.path.join(project_root, "ui", "dist")
    app_path = os.path.join(project_root, "start.py")

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
        "--name",
        "Cornerstone",
        app_path,
    ]

    subprocess.run(args, check=True)

    print("PyInstaller build complete.")


if __name__ == "__main__":
    build_app()
