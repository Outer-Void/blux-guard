"""Smoke tests for BLUX Guard surfaces."""

import tempfile
import sys
from pathlib import Path

import pytest
from typer.testing import CliRunner

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from blux_guard import audit
from blux_guard.cli import bluxq
from blux_guard.tui import app as tui_app

runner = CliRunner()


def test_cli_help() -> None:
    result = runner.invoke(bluxq.app, ["--help"])
    assert result.exit_code == 0
    assert "guard" in result.stdout


def test_tui_instantiation() -> None:
    instance = tui_app.CockpitApp(mode="dev")
    assert instance.mode == "dev"


def test_audit_append(monkeypatch: pytest.MonkeyPatch) -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.setenv("BLUX_GUARD_LOG_DIR", tmpdir)
        cid = audit.record("test.event", actor="test", payload={"foo": "bar"})
        log_path = audit.audit_log_path()
        assert log_path.exists()
        content = log_path.read_text(encoding="utf-8")
        assert cid in content
