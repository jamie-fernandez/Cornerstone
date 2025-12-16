import socket
import subprocess
import time
import webview
import sys
import os
import webview
import os
import sys
import subprocess
import time
import argparse


def check_server_is_ready(port, retries=20, delay=1):
    """
    Checks if a server is listening on a given port.
    """
    for i in range(retries):
        try:
            with socket.create_connection(('localhost', port), timeout=1) as sock:
                print(f'Server is ready on port {port}.')
                return True
        except (socket.timeout, ConnectionRefusedError):
            print(f'Waiting for server on port {port}... (Attempt {i + 1}/{retries})')
            time.sleep(delay)
    return False


def get_html_path():
    """Returns the correct path to the ui, regardless of environment."""
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, 'dist', 'index.html')
    else:
        return 'http://localhost:5173'


if __name__ == '__main__':
    # Check if we are in development mode
    if not getattr(sys, 'frozen', False):
        print('Starting dev environment checks...')
        # Check if the Vue dev server is ready
        if not check_server_is_ready(5173):
            print('Vue dev server failed to start. Exiting.')
            sys.exit(1)

    from app import Api

    api = Api()

    title = f'{api.get_app_configuration()['NAME'].capitalize()}'

    # Launch the pywebview window
    primary_window = webview.create_window(
        title=title,
        url=get_html_path(),
        width=2156,
        height=1309,
        min_size=(800, 600),
        js_api=api
    )

    api.set_window(primary_window)

    webview.start(debug=True)
