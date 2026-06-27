"""Tests for CLI bootstrap environment setup."""

import importlib


class _FakeStream:
    def __init__(self, encoding: str = "cp1252", fail: bool = False) -> None:
        self.encoding = encoding
        self.fail = fail
        self.calls = []

    def reconfigure(self, **kwargs) -> None:
        self.calls.append(kwargs)
        if self.fail:
            raise OSError("cannot reconfigure")
        self.encoding = kwargs.get("encoding", self.encoding)


def test_setup_environment_reconfigures_streams_to_utf8(monkeypatch) -> None:
    """Startup should force UTF-8 with replacement handling on both output streams."""
    bootstrap = importlib.import_module("claude_monitor.cli.bootstrap")
    stdout = _FakeStream()
    stderr = _FakeStream("ascii")

    monkeypatch.setattr(bootstrap.sys, "stdout", stdout)
    monkeypatch.setattr(bootstrap.sys, "stderr", stderr)

    bootstrap.setup_environment()

    assert stdout.calls == [{"encoding": "utf-8", "errors": "replace"}]
    assert stderr.calls == [{"encoding": "utf-8", "errors": "replace"}]


def test_setup_environment_enables_ascii_fallback_when_utf8_unavailable(
    monkeypatch,
) -> None:
    """Windows-style streams that cannot switch to UTF-8 enable ASCII fallback."""
    bootstrap = importlib.import_module("claude_monitor.cli.bootstrap")
    stdout = _FakeStream(fail=True)
    stderr = _FakeStream(fail=True)

    monkeypatch.delenv("CLAUDE_MONITOR_ASCII", raising=False)
    monkeypatch.setattr(bootstrap.sys, "stdout", stdout)
    monkeypatch.setattr(bootstrap.sys, "stderr", stderr)
    monkeypatch.setattr(bootstrap.platform, "system", lambda: "Windows")

    bootstrap.setup_environment()

    assert stdout.calls == [{"encoding": "utf-8", "errors": "replace"}]
    assert stderr.calls == [{"encoding": "utf-8", "errors": "replace"}]
    assert bootstrap.os.environ["CLAUDE_MONITOR_ASCII"] == "1"
