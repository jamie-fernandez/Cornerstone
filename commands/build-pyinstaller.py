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

    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)

    args = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--add-data",
        f"{UI_dist_dir}{os.path.sep};dist",
        "--name",
        "my_app",
        app_path,
    ]

    subprocess.run(args, check=True)

    print("PyInstaller build complete.")


if __name__ == "__main__":
    build_app()
