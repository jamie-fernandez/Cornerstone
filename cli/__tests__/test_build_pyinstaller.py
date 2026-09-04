from __future__ import annotations

import os
import shutil
import subprocess

import pytest

from app.config import CONFIG
from cli.commands import build_pyinstaller


class TestBuildApp:
    def test_aborts_when_ui_dist_is_missing(self, monkeypatch, capsys):
        monkeypatch.setattr(os.path, "exists", lambda path: False)
        monkeypatch.setattr(
            subprocess,
            "run",
            lambda *args, **kwargs: pytest.fail("subprocess.run must not be called"),
        )

        assert build_pyinstaller.build_app() is None

        out = capsys.readouterr().out
        assert "ERROR" in out
        assert "bun run vite build" in out

    def test_cleans_previous_build_directories(self, monkeypatch):
        removed = []
        monkeypatch.setattr(os.path, "exists", lambda path: True)
        monkeypatch.setattr(shutil, "rmtree", lambda path: removed.append(path))
        monkeypatch.setattr(subprocess, "run", lambda args, check: None)

        build_pyinstaller.build_app()

        assert [os.path.basename(path) for path in removed] == ["dist", "build"]

    def test_pyinstaller_args(self, monkeypatch):
        ran = []
        monkeypatch.setattr(os.path, "exists", lambda path: True)
        monkeypatch.setattr(shutil, "rmtree", lambda path: None)
        monkeypatch.setattr(subprocess, "run", lambda args, check: ran.append(args))

        build_pyinstaller.build_app()

        assert len(ran) == 1
        args = ran[0]

        assert args[0] == "pyinstaller"
        assert "--windowed" in args
        assert "--clean" in args
        assert args[args.index("--name") + 1] == CONFIG["NAME"]
        assert args[-1].endswith("start.py")

        # The --add-data separator is ";" on Windows and ":" elsewhere.
        separator = ";" if os.name == "nt" else ":"
        add_data = [args[i + 1] for i, arg in enumerate(args) if arg == "--add-data"]
        assert any(d.endswith(f"{separator}ui/dist") for d in add_data)
        assert any(
            "pyproject.toml" in d and d.endswith(f"{separator}.") for d in add_data
        )
        assert any(d.endswith(f"{separator}app/migrations") for d in add_data)
