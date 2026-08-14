from __future__ import annotations

import json
import os
import shutil
from unittest.mock import patch

from typer.testing import CliRunner

from cli.commands import clean
from cli.common import PROJECT_ROOT
from cli.main import app

runner = CliRunner()


class TestGetBuildArtifacts:
    def test_no_artifacts_exist(self, monkeypatch):
        monkeypatch.setattr(os.path, "exists", lambda path: False)
        monkeypatch.setattr(clean.glob, "glob", lambda pattern: [])

        assert clean.get_build_artifacts() == []

    def test_finds_all_existing_directories_and_spec_files(self, monkeypatch):
        dist_dir = os.path.join(PROJECT_ROOT, "dist")
        build_dir = os.path.join(PROJECT_ROOT, "build")
        ui_dist_dir = os.path.join(PROJECT_ROOT, "ui", "dist")
        spec_file = os.path.join(PROJECT_ROOT, "Cornerstone.spec")

        existing = {dist_dir, build_dir, ui_dist_dir, spec_file}

        monkeypatch.setattr(os.path, "exists", lambda path: path in existing)
        monkeypatch.setattr(os.path, "isfile", lambda path: path in existing)
        monkeypatch.setattr(clean.glob, "glob", lambda pattern: [spec_file])

        artifacts = clean.get_build_artifacts()
        assert artifacts == sorted([dist_dir, build_dir, ui_dist_dir, spec_file])


class TestCleanArtifacts:
    def test_cleans_directories_and_files(self, monkeypatch, capsys):
        dist_dir = os.path.join(PROJECT_ROOT, "dist")
        spec_file = os.path.join(PROJECT_ROOT, "Cornerstone.spec")

        monkeypatch.setattr(clean, "get_build_artifacts", lambda: [dist_dir, spec_file])
        monkeypatch.setattr(os.path, "isdir", lambda path: path == dist_dir)
        monkeypatch.setattr(os.path, "isfile", lambda path: path == spec_file)

        removed_dirs = []
        removed_files = []
        monkeypatch.setattr(shutil, "rmtree", lambda path: removed_dirs.append(path))
        monkeypatch.setattr(os, "remove", lambda path: removed_files.append(path))

        result = clean.clean_artifacts()

        assert removed_dirs == [dist_dir]
        assert removed_files == [spec_file]
        assert result == ["dist", "Cornerstone.spec"]
        out = capsys.readouterr().out
        assert "Cleaning build artifacts..." in out
        assert "Removed directory: dist" in out
        assert "Removed file: Cornerstone.spec" in out
        assert "Clean complete! (2 artifact(s) removed)" in out

    def test_clean_when_no_artifacts(self, monkeypatch, capsys):
        monkeypatch.setattr(clean, "get_build_artifacts", list)

        result = clean.clean_artifacts()

        assert result == []
        out = capsys.readouterr().out
        assert "No build artifacts found to clean" in out

    def test_clean_dry_run(self, monkeypatch, capsys):
        dist_dir = os.path.join(PROJECT_ROOT, "dist")
        monkeypatch.setattr(clean, "get_build_artifacts", lambda: [dist_dir])

        removed_dirs = []
        monkeypatch.setattr(shutil, "rmtree", lambda path: removed_dirs.append(path))

        result = clean.clean_artifacts(dry_run=True)

        assert removed_dirs == []
        assert result == ["dist"]
        out = capsys.readouterr().out
        assert "Build artifacts that would be removed:" in out
        assert "- dist" in out

    def test_clean_json_output(self, monkeypatch, capsys):
        dist_dir = os.path.join(PROJECT_ROOT, "dist")
        monkeypatch.setattr(clean, "get_build_artifacts", lambda: [dist_dir])
        monkeypatch.setattr(os.path, "isdir", lambda path: True)
        monkeypatch.setattr(os.path, "isfile", lambda path: False)

        removed_dirs = []
        monkeypatch.setattr(shutil, "rmtree", lambda path: removed_dirs.append(path))

        result = clean.clean_artifacts(as_json=True)

        assert removed_dirs == [dist_dir]
        assert result == ["dist"]
        out = capsys.readouterr().out
        data = json.loads(out)
        assert data["dry_run"] is False
        assert data["artifacts"] == ["dist"]
        assert data["count"] == 1

    def test_clean_json_dry_run(self, monkeypatch, capsys):
        dist_dir = os.path.join(PROJECT_ROOT, "dist")
        monkeypatch.setattr(clean, "get_build_artifacts", lambda: [dist_dir])

        removed_dirs = []
        monkeypatch.setattr(shutil, "rmtree", lambda path: removed_dirs.append(path))

        result = clean.clean_artifacts(dry_run=True, as_json=True)

        assert removed_dirs == []
        assert result == ["dist"]
        out = capsys.readouterr().out
        data = json.loads(out)
        assert data["dry_run"] is True
        assert data["artifacts"] == ["dist"]
        assert data["count"] == 1


class TestMain:
    def test_main_calls_clean_artifacts(self, monkeypatch):
        called = []
        monkeypatch.setattr(clean, "clean_artifacts", lambda: called.append(True))

        clean.main()
        assert called == [True]


class TestCleanCommandCLI:
    def test_clean_cli_invokes_clean_artifacts(self):
        with patch("cli.commands.clean.clean_artifacts") as mock_clean:
            result = runner.invoke(app, ["clean"])
            assert result.exit_code == 0
            mock_clean.assert_called_once_with(dry_run=False, as_json=False)

    def test_clean_cli_dry_run_option(self):
        with patch("cli.commands.clean.clean_artifacts") as mock_clean:
            result = runner.invoke(app, ["clean", "--dry-run"])
            assert result.exit_code == 0
            mock_clean.assert_called_once_with(dry_run=True, as_json=False)

    def test_clean_cli_json_option(self):
        with patch("cli.commands.clean.clean_artifacts") as mock_clean:
            result = runner.invoke(app, ["clean", "--json"])
            assert result.exit_code == 0
            mock_clean.assert_called_once_with(dry_run=False, as_json=True)

    def test_clean_cli_help(self):
        result = runner.invoke(app, ["clean", "--help"])
        assert result.exit_code == 0
        assert "Clean up build artifacts" in result.stdout
        assert "Examples:" in result.stdout
        assert "--dry-run" in result.stdout
        assert "--json" in result.stdout
