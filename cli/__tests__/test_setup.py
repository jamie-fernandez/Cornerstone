from __future__ import annotations

import subprocess

import pytest

from cli.commands import setup


@pytest.fixture()
def stubbed(monkeypatch):
    """setup() with subprocess/chdir neutralized; returns the run recorder."""
    calls = []
    monkeypatch.setattr("os.chdir", lambda path: None)
    monkeypatch.setattr(
        subprocess, "run", lambda cmd, check=None, shell=None: calls.append(cmd)
    )
    return calls


class TestCheckCommand:
    def test_true_when_found(self, monkeypatch):
        monkeypatch.setattr("shutil.which", lambda cmd: "/usr/bin/bun")

        assert setup.check_command("bun") is True

    def test_false_when_missing(self, monkeypatch):
        monkeypatch.setattr("shutil.which", lambda cmd: None)

        assert setup.check_command("bun") is False


class TestInstallers:
    @pytest.mark.parametrize(
        ("installer", "needles"),
        [
            (
                "install_bun",
                {("darwin", "bun.sh/install"), ("linux", "bun.sh/install")},
            ),
            ("install_uv", {("darwin", "astral.sh/uv"), ("linux", "astral.sh/uv")}),
        ],
    )
    def test_posix_uses_curl_installer(self, stubbed, monkeypatch, installer, needles):
        for platform, needle in needles:
            stubbed.clear()
            monkeypatch.setattr("sys.platform", platform)

            assert getattr(setup, installer)() is True
            assert any(needle in cmd for cmd in stubbed)

    @pytest.mark.parametrize(
        ("installer", "needle"),
        [("install_bun", "bun.sh/install"), ("install_uv", "astral.sh/uv")],
    )
    def test_windows_uses_powershell(self, stubbed, monkeypatch, installer, needle):
        monkeypatch.setattr("sys.platform", "win32")

        assert getattr(setup, installer)() is True
        assert any("powershell" in cmd and needle in cmd for cmd in stubbed)

    def test_failed_install_returns_false(self, monkeypatch):
        def fail(cmd, shell=None, check=None):
            raise subprocess.CalledProcessError(1, cmd)

        monkeypatch.setattr(subprocess, "run", fail)

        assert setup.install_bun() is False
        assert setup.install_uv() is False


class TestSetupFlow:
    def test_installs_dependencies_when_tools_exist(self, stubbed, monkeypatch, capsys):
        monkeypatch.setattr(setup, "check_command", lambda cmd: True)

        setup.setup()

        assert stubbed == [["bun", "install"], ["uv", "sync"]]
        assert "Setup Complete" in capsys.readouterr().out

    def test_exits_when_bun_install_fails(self, stubbed, monkeypatch):
        monkeypatch.setattr(setup, "check_command", lambda cmd: False)
        monkeypatch.setattr(setup, "install_bun", lambda: False)

        with pytest.raises(SystemExit) as exc:
            setup.setup()

        assert exc.value.code == 1
        assert stubbed == []

    def test_exits_when_uv_install_fails(self, stubbed, monkeypatch):
        monkeypatch.setattr(setup, "check_command", lambda cmd: cmd == "bun")
        monkeypatch.setattr(setup, "install_uv", lambda: False)

        with pytest.raises(SystemExit) as exc:
            setup.setup()

        assert exc.value.code == 1
        assert stubbed == []

    def test_uses_default_install_path_after_installing_bun(self, stubbed, monkeypatch):
        monkeypatch.setattr(setup, "check_command", lambda cmd: cmd == "uv")
        monkeypatch.setattr(setup, "install_bun", lambda: True)
        monkeypatch.setattr("os.path.exists", lambda path: True)

        setup.setup()

        bun_cmd, uv_cmd = stubbed
        assert bun_cmd[0].endswith(".bun/bin/bun")
        assert bun_cmd[1:] == ["install"]
        assert uv_cmd == ["uv", "sync"]

    def test_dependency_install_failure_exits(self, monkeypatch, capsys):
        monkeypatch.setattr(setup, "check_command", lambda cmd: True)
        monkeypatch.setattr("os.chdir", lambda path: None)

        def fail(cmd, check=None, shell=None):
            raise subprocess.CalledProcessError(1, cmd)

        monkeypatch.setattr(subprocess, "run", fail)

        with pytest.raises(SystemExit) as exc:
            setup.setup()

        assert exc.value.code == 1
        assert "error occurred during setup" in capsys.readouterr().out
