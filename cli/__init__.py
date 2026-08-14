"""Cornerstone CLI package."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cli.main import app

__all__ = ["app"]


def __getattr__(name: str):
    if name == "app":
        from cli.main import app

        return app
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
