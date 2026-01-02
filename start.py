import os
import socket
import sys
import time

import webview

from app import CONFIG, Api

def check_server_is_ready(port, retries=20, delay=1):
    """
    Checks if a server is listening on a given port.
    """
    for i in range(retries):
        try:
            with socket.create_connection(("localhost", port), timeout=1):
                print(f"Server is ready on port {port}.")
                return True
        except (socket.timeout, ConnectionRefusedError):
            print(f"Waiting for server on port {port}... (Attempt {i + 1}/{retries})")
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
            print(f"Warning: Could not find index.html at {index_path}")
            return os.path.join(base_path, "index.html")
    else:
        return "http://localhost:5173"


if __name__ == "__main__":
    # Check if we are in development mode
    if not getattr(sys, "frozen", False):
        print("Starting dev environment checks...")
        # Check if the Vue dev server is ready
        if not check_server_is_ready(5173):
            print("Vue dev server failed to start. Exiting.")
            sys.exit(1)

    api = Api()

    title = f"{CONFIG['NAME'].capitalize()}"

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
