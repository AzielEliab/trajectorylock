"""CLI: analyze/demo/ui/doctor/version."""

from __future__ import annotations

import json
from pathlib import Path

from trajectorylock import __version__
from trajectorylock.cli import main


def test_cli_version(capsys) -> None:
    assert main(["version"]) == 0
    out = capsys.readouterr().out
    assert f"trajectorylock {__version__}" in out
    assert "Aziel Eliab" in out
    assert __version__ == "0.1.0"


def test_help_lists_commands(capsys) -> None:
    try:
        main(["--help"])
    except SystemExit as exc:
        assert exc.code == 0
    out = capsys.readouterr().out
    for word in ("analyze", "demo", "hash-media", "ui", "doctor", "version"):
        assert word in out


def test_cli_demo(tmp_path: Path, capsys) -> None:
    out = tmp_path / "result.json"
    assert main(["demo", "-o", str(out)]) == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["interpretation"]["certified_instrument"] is False
    assert "not a certified forensic instrument" in data["interpretation"]["guardrail"].lower()
    assert len(data["result_sha256"]) == 64
