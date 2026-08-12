import os
import shutil
import subprocess
import sys


def check_command(command):
    """Check if a command is available in the system."""
    return shutil.which(command) is not None


def install_bun():
    """Install Bun.js based on the operating system."""
    print("\n")
    print("╭─────────────────────────────────────────╮")
    print("│  Installing Bun.js...                   │")
    print("╰─────────────────────────────────────────╯\n")

    try:
        if sys.platform == "darwin" or sys.platform == "linux":
            subprocess.run(
                "curl -fsSL https://bun.sh/install | bash",
                shell=True,
                check=True,
            )
        elif sys.platform == "win32":
            subprocess.run(
                'powershell -c "irm bun.sh/install.ps1 | iex"',
                shell=True,
                check=True,
            )
        print("✓ Bun.js installed successfully\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install Bun.js: {e}")
        return False


def install_uv():
    """Install UV based on the operating system."""
    print("\n")
    print("╭─────────────────────────────────────────╮")
    print("│  Installing UV...                       │")
    print("╰─────────────────────────────────────────╯\n")

    try:
        if sys.platform == "darwin" or sys.platform == "linux":
            subprocess.run(
                "curl -LsSf https://astral.sh/uv/install.sh | sh",
                shell=True,
                check=True,
            )
        elif sys.platform == "win32":
            subprocess.run(
                'powershell -c "irm https://astral.sh/uv/install.ps1 | iex"',
                shell=True,
                check=True,
            )
        print("✓ UV installed successfully\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install UV: {e}")
        return False


def setup():
    """Main setup function to initialize the development environment."""
    try:
        print("\n")
        print("╔═══════════════════════════════════════════╗")
        print("║  Development Environment Setup            ║")
        print("╚═══════════════════════════════════════════╝\n")

        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        os.chdir(project_root)

        # Check and install Bun if needed
        bun_path = "bun"
        if not check_command("bun"):
            print("⚠ Bun.js not found. Installing...")
            if not install_bun():
                print("✗ Bun installation failed. Please install manually: https://bun.sh")
                sys.exit(1)
            # Try to find bun in its default installation path
            home = os.path.expanduser("~")
            potential_bun = os.path.join(home, ".bun", "bin", "bun")
            if os.path.exists(potential_bun):
                bun_path = potential_bun
        else:
            print("✓ Bun.js is already installed\n")

        # Check and install UV if needed
        uv_path = "uv"
        if not check_command("uv"):
            print("⚠ UV not found. Installing...")
            if not install_uv():
                print(
                    "✗ UV installation failed. Please install manually: https://docs.astral.sh/uv/getting-started/installation/"
                )
                sys.exit(1)
            # Try to find uv in its default installation path
            home = os.path.expanduser("~")
            potential_uv = os.path.join(home, ".local", "bin", "uv")
            if os.path.exists(potential_uv):
                uv_path = potential_uv
        else:
            print("✓ UV is already installed\n")

        # Install Node dependencies with Bun
        print("╭─────────────────────────────────────────╮")
        print("│  Installing frontend dependencies...    │")
        print("╰─────────────────────────────────────────╯\n")
        subprocess.run([bun_path, "install"], check=True)
        print("\n✓ Frontend dependencies installed\n")

        # Install Python dependencies with UV
        print("╭─────────────────────────────────────────╮")
        print("│  Installing Python dependencies...      │")
        print("╰─────────────────────────────────────────╯\n")
        subprocess.run([uv_path, "sync"], check=True)
        print("\n✓ Python dependencies installed\n")

        print("╭─────────────────────────────────────────╮")
        print("│  Setup Complete!                        │")
        print("╰─────────────────────────────────────────╯\n")
        print('You can now run "bash commands/start-dev" to start the application.')
    except subprocess.CalledProcessError as e:
        print(f"✗ An error occurred during setup: {e}")
        sys.exit(1)
    except Exception as e:  # noqa: BLE001 - top-level CLI guard: report any failure and exit
        print(f"✗ An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    setup()
