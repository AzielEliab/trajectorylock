"""Command-line interface for TrajectoryLock.

Human sentences are the default. ``--json`` prints the machine record.
Author: Aziel Eliab.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Sequence

from .example import EXAMPLE_CASE
from .integrity import sha256_file
from .pipeline import analyze_case
from .scope import AUTHOR, DEFAULT_PORT, LIMITATION, __version__

UI_URL = f"http://127.0.0.1:{DEFAULT_PORT}/"

WELCOME = f"""TrajectoryLock checks how close a measured line is to a claimed line.

Next, open the workbench on this computer:

  trajectorylock ui

Then open {UI_URL} and press Run check.

  trajectorylock doctor     check this install
  trajectorylock --help     commands

Author: {AUTHOR}
"""

HELP = f"""trajectorylock — check how close a measured line is to a claimed line

usage:
  trajectorylock
  trajectorylock ui
  trajectorylock <command> [--json]

Start
  (no command)     welcome and the next step
  ui               open {UI_URL}

Everyday
  analyze FILE     check a case JSON file
  demo             run the synthetic example
  doctor           self-check on this computer

Other
  version          version and author
  --help           show this message
  --json           machine JSON instead of sentences

Advanced
  hash-media FILE [FILE ...]
                   SHA-256 of evidence files
  server           same as ui
  -o, --output FILE
                   write the JSON receipt (analyze, demo)

Examples
  trajectorylock ui
  trajectorylock demo
  trajectorylock analyze examples/example_case.json
  trajectorylock doctor
  trajectorylock demo --json

Author: {AUTHOR}
"""

_CONCLUSIONS = {
    "consistent_with_declared_tolerances": "Fits the declared tolerances.",
    "inconsistent_with_declared_tolerances": "Does not fit the declared tolerances.",
    "indeterminate": "In between the declared tolerances.",
}


class HumanParser(argparse.ArgumentParser):
    """Plain reasons and a next step, without an argparse usage wall."""

    def error(self, message: str) -> None:
        text = _friendly_error(self.prog, message)
        self.exit(2, text if text.endswith("\n") else text + "\n")


def _friendly_error(prog: str, message: str) -> str:
    choice = re.search(r"invalid choice: '([^']*)'", message)
    if choice:
        name = choice.group(1) or "that"
        return (
            f'Unknown command "{name}".\n'
            "Try: trajectorylock ui    or    trajectorylock --help"
        )
    if "required: case" in message:
        return (
            "A case file is required.\n"
            "Try: trajectorylock demo    or    trajectorylock analyze examples/example_case.json"
        )
    if "required: paths" in message:
        return (
            "Name at least one file to hash.\n"
            "Try: trajectorylock hash-media video.mp4"
        )
    if "required: command" in message or "required: cmd" in message:
        return "Try: trajectorylock ui    or    trajectorylock --help"
    if "invalid int value" in message and "port" in message:
        return "The port needs to be a whole number.\nTry: trajectorylock ui"
    reason = message[:1].upper() + message[1:] if message else "That command could not run"
    if reason and not reason.endswith("."):
        reason += "."
    hint = "trajectorylock --help"
    if prog.endswith(" analyze"):
        hint = "trajectorylock analyze --help"
    elif "hash-media" in prog:
        hint = "trajectorylock hash-media --help"
    elif prog.endswith(" ui") or prog.endswith(" server"):
        hint = "trajectorylock ui --help"
    return f"{reason}\nTry: {hint}"


def _build_parser() -> HumanParser:
    parser = HumanParser(
        prog="trajectorylock",
        usage="trajectorylock [--json] <command> [<args>]",
        description="Checks how close a measured line is to a claimed line.",
    )
    sub = parser.add_subparsers(dest="command", required=False, parser_class=HumanParser)

    analyze = sub.add_parser(
        "analyze",
        help="check a case JSON file",
        description="Check a case JSON file. Sentences are the default. --json prints the machine record.",
    )
    analyze.add_argument("case", help="path to a case JSON file")
    analyze.add_argument("-o", "--output", help="write the JSON receipt to this file")

    demo = sub.add_parser(
        "demo",
        help="run the synthetic example",
        description="Run the synthetic example. Sentences are the default. --json prints the machine record.",
    )
    demo.add_argument("-o", "--output", help="write the JSON receipt to this file")

    hashing = sub.add_parser(
        "hash-media",
        help="SHA-256 of evidence files",
        description="SHA-256 of evidence files. Sentences are the default. --json prints the machine record.",
    )
    hashing.add_argument("paths", nargs="+", help="files to hash")

    for name, help_text in (
        ("ui", f"open the local workbench at {UI_URL}"),
        ("server", "same as ui"),
    ):
        command = sub.add_parser(name, help=help_text, description=help_text)
        command.add_argument("--host", default="127.0.0.1", help="loopback address (default 127.0.0.1)")
        command.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"port (default {DEFAULT_PORT})")

    doctor = sub.add_parser(
        "doctor",
        help="self-check on this computer",
        description="Self-check on this computer. No network. --json prints the machine record.",
    )
    doctor.add_argument("--json", action="store_true", dest="as_json", help=argparse.SUPPRESS)

    sub.add_parser("version", help="version and author", description="Print the version and author.")
    return parser


def _fail(reason: str, hint: str) -> int:
    print(f"{reason}\nTry: {hint}", file=sys.stderr)
    return 2


def _status_payload() -> dict:
    return {
        "name": "trajectorylock",
        "version": __version__,
        "author": AUTHOR,
        "summary": "Checks how close a measured line is to a claimed line.",
        "next": ["trajectorylock ui", "trajectorylock doctor", "trajectorylock --help"],
        "ui": UI_URL,
        "certified_instrument": False,
        "limitation": LIMITATION,
    }


def _pct(value) -> str:
    if value is None:
        return "—"
    return f"{value}%"


def format_result(result: dict, *, synthetic: bool) -> str:
    """Short reading of an analysis record. The JSON record is unchanged."""
    comparison = result.get("official_narrative_comparison") or {}
    confidence = result.get("reconstruction_confidence") or {}
    tolerances = comparison.get("declared_tolerances") or result.get("frozen_tolerances") or {}
    conclusion = _CONCLUSIONS.get(
        comparison.get("conclusion"),
        str(comparison.get("conclusion") or "No reading."),
    )
    lines = [
        f"Case {result.get('case_id', '?')}",
        "",
        "How close is this line to the claimed line",
        f"  Compatibility     {_pct(comparison.get('compatibility_score_percent'))}",
        f"  Match chance      {_pct(comparison.get('threshold_match_probability_percent'))}    P(match | declared model)",
        (
            f"  Evidence          {_pct(confidence.get('confidence_percent'))}"
            f"    independent groups: {confidence.get('independent_group_count', '?')}"
        ),
        "",
        f"Angle difference    {comparison.get('measured_angle_difference_deg', '—')} deg",
        f"Line offset         {comparison.get('measured_line_offset_m', '—')} m",
        f"Tolerances          angle {tolerances.get('angle_deg', '—')} deg, offset {tolerances.get('offset_m', '—')} m",
        f"Reading             {conclusion}",
    ]
    witness = result.get("witness_corroboration") or {}
    if witness.get("count"):
        lines.append(
            f"Witness bearings    {witness.get('count')}    agreement {witness.get('weighted_agreement_percent', '—')}%"
        )
    warnings = result.get("warnings") or []
    if warnings:
        lines.extend(["", "Warnings: " + "; ".join(str(item) for item in warnings)])
    if synthetic or str(result.get("case_id", "")).startswith("SYNTHETIC"):
        lines.extend(["", "Synthetic example. This demonstration is not a real case."])
    lines.extend(
        [
            "",
            f"Result SHA-256      {result.get('result_sha256', '')}",
            "",
            "Full record: add --json",
            f"Author: {AUTHOR}",
        ]
    )
    return "\n".join(lines)


def format_hashes(result: dict) -> str:
    lines = ["SHA-256"]
    for item in result.get("files") or []:
        lines.append(f"  {item.get('path', '?')}")
        lines.append(f"    {item.get('sha256', '?')}    {item.get('size_bytes', '?')} bytes")
    lines.extend(["", "Fingerprint of the file bytes.", "Next: trajectorylock analyze CASE.json", f"Author: {AUTHOR}"])
    return "\n".join(lines)


def _emit_result(result: dict, *, output: str | None, as_json: bool, synthetic: bool) -> int:
    rendered = json.dumps(result, indent=2)
    if output:
        Path(output).write_text(rendered + "\n", encoding="utf-8")
    if as_json:
        print(rendered)
        return 0
    if output:
        print(f"Wrote {output}")
        print("Next: trajectorylock ui")
        return 0
    if "files" in result and "official_narrative_comparison" not in result:
        print(format_hashes(result))
    else:
        print(format_result(result, synthetic=synthetic))
    return 0


def _run_analyze(case_path: str) -> dict:
    path = Path(case_path)
    try:
        raw = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise FileNotFoundError(case_path) from None
    except OSError as exc:
        raise OSError(exc.errno, f"{exc.strerror or exc}: {case_path}") from None
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f'"{case_path}" is not valid JSON ({exc.msg} at line {exc.lineno}).') from None
    if not isinstance(data, dict):
        raise ValueError(f'"{case_path}" must be a JSON object with a case.')
    return analyze_case(data)


def main(argv: Sequence[str] | None = None) -> int:
    raw = list(sys.argv[1:] if argv is None else argv)
    as_json = "--json" in raw
    cleaned = [item for item in raw if item != "--json"]

    if not cleaned:
        if as_json:
            print(json.dumps(_status_payload(), indent=2))
        else:
            print(WELCOME, end="")
        return 0

    if cleaned[0] in ("-h", "--help", "help"):
        print(HELP, end="")
        return 0

    parser = _build_parser()
    try:
        args = parser.parse_args(cleaned)
    except SystemExit as exc:
        code = exc.code
        return int(code) if code is not None else 1

    if args.command is None:
        if as_json:
            print(json.dumps(_status_payload(), indent=2))
        else:
            print(WELCOME, end="")
        return 0

    if getattr(args, "as_json", False):
        as_json = True

    if args.command == "version":
        if as_json:
            print(json.dumps({"name": "trajectorylock", "version": __version__, "author": AUTHOR}, indent=2))
        else:
            print(f"trajectorylock {__version__}")
            print(f"author {AUTHOR}")
        return 0

    if args.command == "doctor":
        from .doctor import run_doctor

        return run_doctor(as_json=as_json)

    if args.command in ("ui", "server"):
        from .server import serve

        host = getattr(args, "host", "127.0.0.1")
        port = getattr(args, "port", DEFAULT_PORT)
        try:
            serve(host=host, port=port)
        except ValueError as exc:
            return _fail(str(exc), "trajectorylock ui")
        except OSError as exc:
            return _fail(
                f"Can't open {host}:{port} ({exc.strerror or exc}).",
                "trajectorylock ui --port 8875",
            )
        return 0

    try:
        if args.command == "analyze":
            result = _run_analyze(args.case)
            synthetic = str(result.get("case_id", "")).startswith("SYNTHETIC")
        elif args.command == "demo":
            result = analyze_case(EXAMPLE_CASE)
            synthetic = True
        elif args.command == "hash-media":
            result = {"files": [sha256_file(path) for path in args.paths], "limitation": LIMITATION}
            synthetic = False
        else:
            return _fail(f'Unknown command "{args.command}".', "trajectorylock --help")
    except FileNotFoundError:
        target = getattr(args, "case", None) or (args.paths[0] if getattr(args, "paths", None) else "that file")
        return _fail(f'Can\'t read "{target}" — no such file.', "trajectorylock demo")
    except OSError as exc:
        return _fail(str(exc), "trajectorylock --help")
    except ValueError as exc:
        return _fail(str(exc), "trajectorylock demo")

    output = getattr(args, "output", None)
    return _emit_result(result, output=output, as_json=as_json, synthetic=synthetic)


if __name__ == "__main__":
    raise SystemExit(main())
