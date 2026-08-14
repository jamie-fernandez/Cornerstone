from __future__ import annotations

import subprocess

import pytest

from cli.commands import dev


class FakeProc:
    """Stand-in for subprocess.Popen: records lifecycle calls, never spawns."""

    def __init__(self, returncode=0, hang=False):
        self.returncode = returncode
        self.hang = hang
        self.terminated = False
        self.killed = False
        self.wait_calls = []

    def terminate(self):
        self.terminated = True

    def wait(self, timeout=None):
        self.wait_calls.append(timeout)
        if self.hang:
            raise subprocess.TimeoutExpired(cmd="fake", timeout=timeout)
        return self.returncode

    def kill(self):
        self.killed = True


@pytest.fixture()
def clean_dev(monkeypatch):
    """dev module with the process list reset and side effects stubbed."""
    monkeypatch.setattr(dev, "_processes", [])
    monkeypatch.setattr("signal.signal", lambda sig, handler: None)
    monkeypatch.setattr("os.chdir", lambda path: None)
    return dev


class TestShutdown:
    def test_terminates_and_waits_for_all_children(self, clean_dev, capsys):
        procs = [FakeProc(), FakeProc()]
        clean_dev._processes.extend(procs)

        with pytest.raises(SystemExit) as exc:
            clean_dev._shutdown(None, None)

        assert exc.value.code == 0
        assert all(p.terminated for p in procs)
        assert all(p.wait_calls == [5] for p in procs)
        assert not any(p.killed for p in procs)
        assert "Shutting down development servers" in capsys.readouterr().out

    def test_kills_children_that_ignore_terminate(self, clean_dev):
        stubborn = FakeProc(hang=True)
        clean_dev._processes.append(stubborn)

        with pytest.raises(SystemExit) as exc:
            clean_dev._shutdown(None, None)

        assert exc.value.code == 0
        assert stubborn.terminated
        assert stubborn.killed


class TestMain:
    def test_starts_frontend_and_backend(self, clean_dev, monkeypatch, capsys):
        spawned = []

        def fake_popen(cmd):
            proc = FakeProc()
            spawned.append(cmd)
            return proc

        monkeypatch.setattr("subprocess.Popen", fake_popen)

        with pytest.raises(SystemExit) as exc:
            clean_dev.main()

        assert exc.value.code == 0
        assert [cmd[0].rsplit("/", 1)[-1] for cmd in spawned] == ["bun", "uv"]
        assert [cmd[1:] for cmd in spawned] == [["run", "dev"], ["run", "start.py"]]
        assert "Starting development environment" in capsys.readouterr().out

    def test_propagates_first_failing_child_exit_code(self, clean_dev, monkeypatch):
        procs = iter([FakeProc(returncode=0), FakeProc(returncode=42)])
        monkeypatch.setattr("subprocess.Popen", lambda cmd: next(procs))

        with pytest.raises(SystemExit) as exc:
            clean_dev.main()

        assert exc.value.code == 42

    def test_all_zero_exit_codes_exit_zero(self, clean_dev, monkeypatch):
        procs = iter([FakeProc(returncode=0), FakeProc(returncode=0)])
        monkeypatch.setattr("subprocess.Popen", lambda cmd: next(procs))

        with pytest.raises(SystemExit) as exc:
            clean_dev.main()

        assert exc.value.code == 0
