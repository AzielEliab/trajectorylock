"""Command-line interface for TrajectoryLock.

    trajectorylock analyze CASE.json -o result.json
    trajectorylock demo -o result.json
    trajectorylock hash-media video.mp4 photo.jpg
    trajectorylock ui
    trajectorylock doctor
    trajectorylock version
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .example import EXAMPLE_CASE
from .integrity import sha256_file
from .pipeline import analyze_case
from .scope import AUTHOR, DEFAULT_PORT, LIMITATION, __version__


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trajectorylock",
        description="TrajectoryLock v0.1 — auditable geometric trajectory test. Research prototype.",
        epilog=LIMITATION,
    )
    sub = parser.add_subparsers(dest="command", required=True)
    analyze = sub.add_parser("analyze", help="analyze a case JSON file")
    analyze.add_argument("case")
    analyze.add_argument("-o", "--output")
    demo = sub.add_parser("demo", help="run the synthetic demonstration (not a real case)")
    demo.add_argument("-o", "--output")
    hashing = sub.add_parser("hash-media", help="SHA-256 hash evidence files")
    hashing.add_argument("paths", nargs="+")
    p_ui = sub.add_parser("ui", help=f"Serve the local UI on 127.0.0.1:{DEFAULT_PORT} (loopback only).")
    p_ui.add_argument("--host", default="127.0.0.1")
    p_ui.add_argument("--port", type=int, default=DEFAULT_PORT)
    p_doc = sub.add_parser("doctor", help="Self-check: geometry, independence, guardrail, loopback. No network.")
    p_doc.add_argument("--json", action="store_true", dest="as_json")
    sub.add_parser("server", help="Alias of ui (loopback workbench).")
    sub.add_parser("version", help="Print package version.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.command == "version":
        print(f"trajectorylock {__version__}")
        print(f"author {AUTHOR}")
        return 0

    if args.command == "doctor":
        from .doctor import run_doctor

        return run_doctor(as_json=args.as_json)

    if args.command in ("ui", "server"):
        from .server import serve

        host = getattr(args, "host", "127.0.0.1")
        port = getattr(args, "port", DEFAULT_PORT)
        serve(host=host, port=port)
        return 0

    if args.command == "analyze":
        data = json.loads(Path(args.case).read_text(encoding="utf-8"))
        result = analyze_case(data)
    elif args.command == "demo":
        result = analyze_case(EXAMPLE_CASE)
    elif args.command == "hash-media":
        result = {"files": [sha256_file(path) for path in args.paths], "limitation": LIMITATION}
    else:
        parser.error(f"unknown command {args.command}")
        return 2

    rendered = json.dumps(result, indent=2)
    output = getattr(args, "output", None)
    if output:
        Path(output).write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
