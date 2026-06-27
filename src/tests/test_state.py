"""Tests for the atomic state-file writer (#184)."""

import json
from pathlib import Path

from claude_monitor.output.state import default_state_path, write_state_file


def test_write_state_file_roundtrip_and_creates_dir(tmp_path: Path) -> None:
    snap = {"schema_version": "1.0", "nums": [1, 2, 3], "nested": {"a": None}}
    path = tmp_path / "state" / "latest.json"  # parent does not exist yet

    write_state_file(snap, path)

    assert path.exists()
    assert json.loads(path.read_text()) == snap


def test_write_state_file_leaves_no_temp(tmp_path: Path) -> None:
    path = tmp_path / "latest.json"
    write_state_file({"x": 1}, path)
    assert not path.with_name("latest.json.tmp").exists()


def test_write_state_file_overwrites_existing(tmp_path: Path) -> None:
    path = tmp_path / "latest.json"
    write_state_file({"v": 1}, path)
    write_state_file({"v": 2}, path)
    assert json.loads(path.read_text()) == {"v": 2}


def test_default_state_path() -> None:
    p = default_state_path()
    assert p.name == "latest.json"
    assert ".claude-monitor" in str(p)
