import os
import socket
import sys
import time

import typer
import webview

from app import API, CONFIG
from app.database import init_db


def check_server_is_ready(port, retries=20, delay=1):
    """
    Checks if a server is listening on a given port.
    """
    for i in range(retries):
        try:
            with socket.create_connection(("localhost", port), timeout=1):
                typer.secho(f"✓ Server is ready on port {port}.", fg=typer.colors.GREEN)
                return True
        except (TimeoutError, ConnectionRefusedError):
            typer.secho(
                f"Waiting for server on port {port}... (Attempt {i + 1}/{retries})",
                fg=typer.colors.YELLOW,
            )
            time.sleep(delay)
    return False


def get_html_path():
    """Returns the correct path to the ui, regardless of environment."""
    if getattr(sys, "frozen", False):
        base_path = sys._MEIPASS
        index_path = os.path.join(base_path, "ui", "dist", "index.html")

        if os.path.exists(index_path):
            return index_path
        else:
            typer.secho(
                f"Warning: Could not find index.html at {index_path}",
                fg=typer.colors.YELLOW,
                bold=True,
            )
            return os.path.join(base_path, "index.html")
    else:
        return "http://localhost:5173"


if __name__ == "__main__":
    # Check if we are in development mode
    if not getattr(sys, "frozen", False):
        typer.secho(
            "Starting dev environment checks...", fg=typer.colors.CYAN, bold=True
        )
        # Check if the Vue dev server is ready
        if not check_server_is_ready(5173):
            typer.secho(
                "✗ Vue dev server failed to start. Exiting.",
                fg=typer.colors.RED,
                bold=True,
            )
            sys.exit(1)

    init_db()

    api = API()

    title = CONFIG["NAME"]

    # Launch the pywebview window
    primary_window = webview.create_window(
        title=title,
        url=get_html_path(),
        width=2156,
        height=1309,
        min_size=(800, 600),
        js_api=api,
    )

    api.set_window(primary_window)

    webview.start(debug=True)
