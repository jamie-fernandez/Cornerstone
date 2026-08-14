"""Shared helpers and constants for the CLI package."""

from __future__ import annotations

import os
import shutil

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Default install locations used by the Bun/UV installers when they are not on PATH.
BUN_DEFAULT = os.path.join(os.path.expanduser("~"), ".bun", "bin", "bun")
UV_DEFAULT = os.path.join(os.path.expanduser("~"), ".local", "bin", "uv")


def find_executable(cmd: str, default_path: str) -> str:
    """Resolve ``cmd`` from PATH, falling back to ``default_path`` when it exists.

    Installers for Bun/UV put binaries in user-local locations that may not be
    on PATH yet (e.g. ``~/.bun/bin/bun``). When neither resolves, return ``cmd``
    unchanged so the caller's error is the familiar "command not found".
    """
    if shutil.which(cmd):
        return cmd
    if os.path.isfile(default_path):
        return default_path
    return cmd
