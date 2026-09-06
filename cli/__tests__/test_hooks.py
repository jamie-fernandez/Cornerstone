from __future__ import annotations

import os
import stat

import pytest
from typer.testing import CliRunner

from cli.commands import hooks
from cli.main import app

runner = CliRunner()


@pytest.fixture()
def git_repo(tmp_path, monkeypatch):
    """Set up temporary repo with .git folder."""
    monkeypatch.setattr(hooks, "PROJECT_ROOT", str(tmp_path))
    (tmp_path / ".git").mkdir(parents=True, exist_ok=True)
    return tmp_path


class TestGitHooks:
    def test_install_and_uninstall_hook(self, git_repo):
        # Install
        result = runner.invoke(app, ["hooks", "install"])
        assert result.exit_code == 0
        assert "Pre-commit hook installed successfully" in result.stdout

        hook_file = git_repo / ".git" / "hooks" / "pre-commit"
        assert hook_file.exists()
        assert "Ruff" in hook_file.read_text()
        assert "Biome" in hook_file.read_text()

        # Check executable bit
        mode = os.stat(str(hook_file)).st_mode
        assert bool(mode & stat.S_IXUSR)

        # Uninstall
        result_un = runner.invoke(app, ["hooks", "uninstall"])
        assert result_un.exit_code == 0
        assert "Pre-commit hook removed" in result_un.stdout
        assert not hook_file.exists()

    def test_install_without_git_repo(self, tmp_path, monkeypatch):
        monkeypatch.setattr(hooks, "PROJECT_ROOT", str(tmp_path))
        result = runner.invoke(app, ["hooks", "install"])
        assert result.exit_code != 0
        assert "Not a Git repository" in result.stdout
