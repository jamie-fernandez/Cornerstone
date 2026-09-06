from __future__ import annotations

import json
import sys
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from cli.commands import doctor
from cli.main import app

runner = CliRunner()


class TestDoctorChecks:
    def test_check_python_version_ok(self):
        check = doctor.check_python_version()
        assert check["name"] == "Python Runtime"
        assert check["status"] == "ok"
        assert "meets requirement" in check["details"]

    def test_check_python_version_error(self, monkeypatch):
        monkeypatch.setattr(sys, "version_info", (3, 12, 0, "final", 0))
        monkeypatch.setattr(doctor.platform, "python_version", lambda: "3.12.0")
        check = doctor.check_python_version()
        assert check["status"] == "error"
        assert "below required version" in check["details"]
        assert check["remediation"] is not None

    def test_check_uv_found(self, monkeypatch):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="uv 0.6.0\n", returncode=0)
            with patch("shutil.which", return_value="/usr/local/bin/uv"):
                check = doctor.check_uv()
                assert check["status"] == "ok"
                assert check["value"] == "uv 0.6.0"

    def test_check_uv_missing(self):
        with (
            patch("shutil.which", return_value=None),
            patch("os.path.isfile", return_value=False),
        ):
            check = doctor.check_uv()
            assert check["status"] == "error"
            assert "Not found" in check["value"]
            assert check["remediation"] is not None

    def test_check_bun_found(self):
        with (
            patch("subprocess.run") as mock_run,
            patch("shutil.which", return_value="/usr/local/bin/bun"),
        ):
            mock_run.return_value = MagicMock(stdout="1.3.0\n", returncode=0)
            check = doctor.check_bun()
            assert check["status"] == "ok"
            assert "v1.3.0" in check["value"]

    def test_check_bun_missing(self):
        with (
            patch("shutil.which", return_value=None),
            patch("os.path.isfile", return_value=False),
        ):
            check = doctor.check_bun()
            assert check["status"] == "error"
            assert check["remediation"] is not None

    def test_check_gui_engine_darwin(self, monkeypatch):
        monkeypatch.setattr(sys, "platform", "darwin")
        check = doctor.check_gui_engine()
        assert check["status"] == "ok"
        assert "macOS WebKit" in check["value"]

    def test_check_gui_engine_windows(self, monkeypatch):
        monkeypatch.setattr(sys, "platform", "win32")
        check = doctor.check_gui_engine()
        assert check["status"] == "ok"
        assert "Windows WebView2" in check["value"]

    def test_check_gui_engine_linux_headless(self, monkeypatch):
        monkeypatch.setattr(sys, "platform", "linux")
        monkeypatch.delenv("DISPLAY", raising=False)
        monkeypatch.delenv("WAYLAND_DISPLAY", raising=False)
        check = doctor.check_gui_engine()
        assert check["status"] in ("warning", "error")

    def test_check_database_ok(self):
        check = doctor.check_database()
        assert check["status"] in ("ok", "warning")
        assert "SQLite" in check["name"]

    def test_check_git(self):
        check = doctor.check_git()
        assert check["name"] == "Git Version Control"


class TestDoctorCommand:
    def test_doctor_cli_text(self):
        result = runner.invoke(app, ["doctor"])
        assert "Cornerstone Environment & Dependency Diagnostics" in result.stdout

    def test_doctor_cli_json(self):
        result = runner.invoke(app, ["doctor", "--json"])
        data = json.loads(result.stdout)
        assert "healthy" in data
        assert "checks" in data
        assert isinstance(data["checks"], list)
