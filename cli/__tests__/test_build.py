from __future__ import annotations

import subprocess

import pytest

from cli.commands import build
from cli.common import PROJECT_ROOT


class TestBuildSteps:
    """The default steps must match the workflow the old bash script ran."""

    def test_frontend_then_backend(self):
        labels = [label for label, _ in build.BUILD_STEPS]

        assert labels == ["frontend", "backend executable"]

    def test_frontend_step_is_vite_build(self):
        frontend_cmd = build.BUILD_STEPS[0][1]

        assert frontend_cmd[0].endswith("bun")
        assert frontend_cmd[1:] == ["run", "vite", "build"]

    def test_backend_step_is_pyinstaller_script(self):
        backend_cmd = build.BUILD_STEPS[1][1]

        assert backend_cmd[0].endswith("uv")
        assert backend_cmd[1:] == [
            "run",
            "-m",
            "cli.commands.build_pyinstaller",
        ]


class TestMain:
    def test_runs_all_steps_in_order(self, monkeypatch, capsys):
        calls = []
        steps = [("one", ["a", "1"]), ("two", ["b", "2"])]
        monkeypatch.setattr(build, "BUILD_STEPS", steps)
        monkeypatch.setattr("os.chdir", lambda path: calls.append(("chdir", path)))
        monkeypatch.setattr(
            "subprocess.run", lambda cmd, check: calls.append(("run", cmd, check))
        )

        build.main()

        assert calls == [
            ("chdir", PROJECT_ROOT),
            ("run", ["a", "1"], True),
            ("run", ["b", "2"], True),
        ]
        assert "Build complete!" in capsys.readouterr().out

    def test_failed_step_exits_nonzero_and_stops(self, monkeypatch, capsys):
        calls = []

        def fail(cmd, check):
            calls.append(cmd)
            raise subprocess.CalledProcessError(3, cmd)

        steps = [("one", ["bad", "cmd"]), ("two", ["never", "runs"])]
        monkeypatch.setattr(build, "BUILD_STEPS", steps)
        monkeypatch.setattr("os.chdir", lambda path: None)
        monkeypatch.setattr("subprocess.run", fail)

        with pytest.raises(SystemExit) as exc:
            build.main()

        assert exc.value.code == 1
        assert calls == [["bad", "cmd"]]
        out = capsys.readouterr().out
        assert "Build failed" in out
        assert "code 3" in out
