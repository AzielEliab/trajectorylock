"""Dependency-light local HTTP workbench. Loopback by default (127.0.0.1:8874)."""

from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from .example import EXAMPLE_CASE
from .integrity import canonical_hash, sha256_file
from .pipeline import analyze_case
from .scope import AUTHOR, DEFAULT_PORT, GUARDRAIL, LIMITATION, LOOPBACK, SPEC, __version__

STATIC = Path(__file__).with_name("static")
MAX_BODY = 10_000_000


class Handler(BaseHTTPRequestHandler):
    server_version = "TrajectoryLock/0.1"

    def _json(self, status: int, payload) -> None:
        body = json.dumps(payload, indent=2).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _bytes(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _body(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length > MAX_BODY:
            raise ValueError("request exceeds 10 MB")
        return json.loads(self.rfile.read(length) or b"{}")

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/health":
            return self._json(
                200,
                {
                    "status": "ok",
                    "ok": True,
                    "version": __version__,
                    "spec": SPEC,
                    "loopback": True,
                    "telemetry": False,
                    "certified_instrument": False,
                    "author": AUTHOR,
                    "limitation": LIMITATION,
                    "guardrail": GUARDRAIL,
                },
            )
        if path == "/api/example":
            return self._json(200, EXAMPLE_CASE)
        if path == "/api/doctor":
            from .doctor import run_doctor
            import io
            import contextlib

            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                code = run_doctor(as_json=True)
            payload = json.loads(buf.getvalue() or "{}")
            payload["exit_code"] = code
            return self._json(200 if code == 0 else 500, payload)
        if path in ("/", "/index.html"):
            return self._bytes(200, (STATIC / "index.html").read_bytes(), "text/html; charset=utf-8")
        if path == "/style.css" and (STATIC / "style.css").is_file():
            return self._bytes(200, (STATIC / "style.css").read_bytes(), "text/css; charset=utf-8")
        self._json(404, {"error": "not found"})

    def do_POST(self):
        try:
            body = self._body()
            path = urlparse(self.path).path
            if path == "/api/analyze":
                result = analyze_case(body)
                return self._json(200, result)
            if path == "/api/hash":
                return self._json(200, {"files": [sha256_file(p) for p in body.get("paths", [])]})
            if path == "/api/fingerprint":
                case = body.get("case", body)
                return self._json(
                    200,
                    {
                        "sha256": canonical_hash(case),
                        "certified_instrument": False,
                        "guardrail": GUARDRAIL,
                    },
                )
            self._json(404, {"error": "not found"})
        except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
            self._json(400, {"error": str(exc), "guardrail": GUARDRAIL})
        except Exception:  # pragma: no cover - server boundary
            self._json(500, {"error": "internal error", "guardrail": GUARDRAIL})

    def log_message(self, fmt, *args):
        print(f"{self.address_string()} - {fmt % args}")


def make_server(host: str, port: int) -> ThreadingHTTPServer:
    if host not in LOOPBACK:
        raise ValueError(f"UI binds loopback only ({', '.join(sorted(LOOPBACK))}); refused {host!r}")
    return ThreadingHTTPServer((host, port), Handler)


def serve(host: str = "127.0.0.1", port: int = DEFAULT_PORT) -> None:
    server = make_server(host, port)
    print(f"TrajectoryLock workbench: http://{host}:{port}")
    print(LIMITATION)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="TrajectoryLock local workbench (loopback).")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument(
        "--allow-non-loopback",
        action="store_true",
        help="Permit non-loopback bind (Docker). Default refuses 0.0.0.0.",
    )
    args = parser.parse_args(argv)
    if args.allow_non_loopback:
        server = ThreadingHTTPServer((args.host, args.port), Handler)
        print(f"TrajectoryLock workbench (non-loopback): http://{args.host}:{args.port}")
        print(LIMITATION)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()
        return 0
    serve(host=args.host, port=args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
