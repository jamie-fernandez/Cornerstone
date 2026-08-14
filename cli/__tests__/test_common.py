from __future__ import annotations

import os

from cli.common import BUN_DEFAULT, UV_DEFAULT, find_executable


class TestFindExecutable:
    def test_returns_command_when_on_path(self, monkeypatch):
        monkeypatch.setattr("shutil.which", lambda cmd: f"/usr/bin/{cmd}")

        assert find_executable("bun", "/nonexistent/bun") == "bun"

    def test_falls_back_to_default_path(self, monkeypatch, tmp_path):
        monkeypatch.setattr("shutil.which", lambda cmd: None)
        default = tmp_path / "bun"
        default.touch()

        assert find_executable("bun", str(default)) == str(default)

    def test_falls_back_to_bare_command_when_missing_everywhere(
        self, monkeypatch, tmp_path
    ):
        monkeypatch.setattr("shutil.which", lambda cmd: None)

        assert find_executable("bun", str(tmp_path / "nope")) == "bun"

    def test_default_paths_point_into_home(self):
        home = os.path.expanduser("~")

        assert BUN_DEFAULT == os.path.join(home, ".bun", "bin", "bun")
        assert UV_DEFAULT == os.path.join(home, ".local", "bin", "uv")
