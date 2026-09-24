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


def test_bare_command_welcomes(capsys) -> None:
    assert main([]) == 0
    out = capsys.readouterr().out
    assert "trajectorylock ui" in out
    assert "Run check" in out
    assert "Aziel Eliab" in out
    assert "arguments are required" not in out
    assert not out.lstrip().startswith("{")


def test_help_is_short(capsys) -> None:
    assert main(["--help"]) == 0
    out = capsys.readouterr().out
    assert "Examples" in out
    assert "hash-media" in out
    assert "--json" in out
    assert "THIS IS NOT" not in out


def test_unknown_command_has_next_step(capsys) -> None:
    assert main(["bogus"]) == 2
    err = capsys.readouterr().err
    assert 'Unknown command "bogus".' in err
    assert "trajectorylock --help" in err
    assert "Traceback" not in err


def test_missing_case_has_next_step(capsys) -> None:
    assert main(["analyze", "no-such-case.json"]) == 2
    err = capsys.readouterr().err
    assert "no-such-case.json" in err
    assert "trajectorylock demo" in err
    assert "Traceback" not in err


def test_bad_json_has_next_step(tmp_path: Path, capsys) -> None:
    case = tmp_path / "bad.json"
    case.write_text("{", encoding="utf-8")
    assert main(["analyze", str(case)]) == 2
    err = capsys.readouterr().err
    assert "not valid JSON" in err
    assert "trajectorylock demo" in err


def test_demo_json_and_human(capsys) -> None:
    assert main(["demo", "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["schema_version"] == "trajectorylock-result-0.1"
    assert data["interpretation"]["certified_instrument"] is False
    assert "official_narrative_comparison" in data
    assert main(["demo"]) == 0
    out = capsys.readouterr().out
    assert "How close is this line to the claimed line" in out
    assert "Compatibility" in out
    assert "Aziel Eliab" in out
    assert not out.lstrip().startswith("{")


def test_doctor_json_flag(capsys) -> None:
    assert main(["doctor", "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["ok"] is True
    assert data["certified_instrument"] is False
    assert isinstance(data["checks"], list)
    assert "plain" in data
