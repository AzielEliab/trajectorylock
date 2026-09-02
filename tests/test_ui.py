"""Local UI: one screen (load JSON, run check, see result), Import+Export, guardrail, no CDN."""

from __future__ import annotations

import json
import threading
import urllib.request

import pytest

from trajectorylock.server import LOOPBACK, make_server


def test_ui_rejects_non_loopback() -> None:
    with pytest.raises(ValueError, match="loopback"):
        make_server("0.0.0.0", 9)
    assert "127.0.0.1" in LOOPBACK


def _serve():
    httpd = make_server("127.0.0.1", 0)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return httpd


def test_ui_get_root_honest_scope() -> None:
    httpd = _serve()
    port = httpd.server_address[1]
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=5) as resp:
            html = resp.read().decode("utf-8")
        assert "TrajectoryLock" in html
        assert "THIS IS" in html
        assert "THIS IS NOT" in html
        assert "certified forensic instrument" in html.lower()
        assert "shooter" in html.lower()
        assert "intent" in html.lower()
        assert "guilt" in html.lower()
        assert "Load example" in html
        assert "Run check" in html
        assert "Import" in html
        assert "Export" in html
        assert "Verify" in html
        assert "Doctor" in html
        assert "how close is this line to the claimed line" in html.lower()
        assert "cdnjs" not in html.lower()
        assert "unpkg" not in html.lower()
        assert "jsdelivr" not in html.lower()
        assert ("GodLock" + ".AZ") not in html
        assert "10.5281/zenodo.22258015" in html
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/health", timeout=3) as resp:
            health = json.loads(resp.read().decode("utf-8"))
        assert health["ok"] is True
        assert health["loopback"] is True
        assert health["telemetry"] is False
        assert health["certified_instrument"] is False
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/example", timeout=3) as resp:
            example = json.loads(resp.read().decode("utf-8"))
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/api/analyze",
            data=json.dumps({**example, "analysis": {**example.get("analysis", {}), "monte_carlo_samples": 200}}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        assert result["interpretation"]["certified_instrument"] is False
        assert "not a certified forensic instrument" in result["interpretation"]["guardrail"].lower()
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/doctor", timeout=20) as resp:
            doctor = json.loads(resp.read().decode("utf-8"))
        assert doctor["ok"] is True
        assert "not a certified forensic instrument" in doctor["plain"].lower()
        assert "shooter" in doctor["plain"].lower()
        assert "intent" in doctor["plain"].lower()
        assert "guilt" in doctor["plain"].lower()
    finally:
        httpd.shutdown()
        httpd.server_close()
