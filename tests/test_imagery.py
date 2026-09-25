"""Satellite frames: real bytes when the source answers, and an honest gap when it does not."""

from __future__ import annotations

import base64
import hashlib
import json
import threading
import urllib.request

import pytest

from trajectorylock.example import EXAMPLE_CASE
from trajectorylock.imagery import pull_for_case, pull_imagery, review_case
from trajectorylock.server import make_server

JPEG = b"\xff\xd8\xff\xd9"
OTHER = b"\xff\xd8\xff\x00other-frame"


def _http(status: int, body: bytes, content_type: str = "image/jpeg"):
    def fetch(url: str, timeout: float = 12):
        return status, content_type, body

    return fetch


def test_same_day_returns_the_fetched_bytes_only() -> None:
    seen = []

    def fetch(url: str, timeout: float = 12):
        seen.append(url)
        assert "MODIS_Terra_CorrectedReflectance_TrueColor" in url
        assert "2024-08-15" in url
        assert "gibs.earthdata.nasa.gov" in url
        return 200, "image/jpeg", JPEG

    info = pull_imagery(latitude=37.0, longitude=-122.0, when="2024-08-15T18:30:00Z", place="Synthetic example point", fetch=fetch)
    assert info["ok"] is True
    assert info["source"] == "NASA GIBS"
    assert info["relation"] == "same_calendar_day"
    assert info["frame_time"] == "2024-08-15"
    assert info["time_delta_seconds"] != 0
    assert "not a photograph at the event minute" in info["summary"]
    assert "NASA GIBS" in info["summary"]
    assert base64.b64decode(info["image_base64"]) == JPEG
    assert info["image_sha256"] == hashlib.sha256(JPEG).hexdigest()
    assert len(seen) == 1


def test_nearest_frame_states_source_and_time_delta() -> None:
    def fetch(url: str, timeout: float = 12):
        if "2024-08-15" in url:
            return 404, "text/html", b"<html>missing</html>"
        if "2024-08-16" in url:
            return 200, "image/jpeg", OTHER
        return 404, "text/html", b"no"

    info = pull_imagery(latitude=37.0, longitude=-122.0, when="2024-08-15T18:30:00Z", fetch=fetch)
    assert info["ok"] is True
    assert info["relation"] == "nearest"
    assert info["frame_time"] == "2024-08-16"
    assert info["time_delta_seconds"] > 0
    assert "NASA GIBS" in info["summary"]
    assert "2024-08-16" in info["summary"]
    assert "2024-08-15" in info["summary"]
    assert "after the event time" in info["summary"]
    assert base64.b64decode(info["image_base64"]) == OTHER
    assert b"<html>" not in base64.b64decode(info["image_base64"])


def test_missing_archive_has_no_image_bytes() -> None:
    info = pull_imagery(
        latitude=37.0,
        longitude=-122.0,
        when="2024-08-15T18:30:00Z",
        fetch=_http(404, b"<html>no</html>", "text/html"),
        search_days=1,
    )
    assert info["ok"] is False
    assert info["relation"] == "missing"
    assert info["image_base64"] is None
    assert info["image_sha256"] is None
    assert info["source"] == "NASA GIBS"
    assert "No image is shown" in info["summary"]
    assert info["next_step"]


def test_source_down_has_no_stand_in() -> None:
    def fetch(url: str, timeout: float = 12):
        raise ConnectionError("network unreachable")

    info = pull_imagery(latitude=10.0, longitude=20.0, when="2024-01-02T00:00:00Z", fetch=fetch)
    assert info["ok"] is False
    assert info["image_base64"] is None
    assert "NASA GIBS" in info["summary"]
    assert "No image is shown" in info["summary"]
    assert "gibs.earthdata.nasa.gov" in info["next_step"]


def test_place_name_uses_nominatim_then_the_tile() -> None:
    def fetch(url: str, timeout: float = 12):
        if "nominatim.openstreetmap.org" in url:
            body = json.dumps([{"lat": "37.0", "lon": "-122.0"}]).encode()
            return 200, "application/json", body
        assert "/8/" in url
        return 200, "image/jpeg", JPEG

    info = pull_imagery(latitude=None, longitude=None, when="2024-08-15T18:30:00Z", place="Synthetic example point", fetch=fetch)
    assert info["ok"] is True
    assert info["geocode_source"] == "OpenStreetMap Nominatim"
    assert info["latitude"] == pytest.approx(37.0)
    assert info["longitude"] == pytest.approx(-122.0)
    assert "OpenStreetMap Nominatim" in info["summary"]
    assert base64.b64decode(info["image_base64"]) == JPEG


def test_review_keeps_geometry_separate_from_the_frame() -> None:
    case = json.loads(json.dumps(EXAMPLE_CASE))
    case["analysis"] = {"monte_carlo_samples": 200, "random_seed": 23}
    review = review_case(case, fetch=_http(200, JPEG))
    assert "image_base64" not in review["result"]
    assert review["result"]["interpretation"]["certified_instrument"] is False
    assert review["imagery"]["image_sha256"] == hashlib.sha256(JPEG).hexdigest()
    assert "beside the satellite frame" in review["summary"]
    assert "NASA GIBS" in review["summary"]


def test_case_without_place_or_time_does_not_invent_a_frame() -> None:
    info = pull_for_case({"case_id": "PLAIN", "sources": [], "observations": [], "official_hypothesis": {}})
    assert info["attempted"] is False
    assert info["image_base64"] is None


def test_review_endpoint_and_analyze_stays_geometric(monkeypatch) -> None:
    monkeypatch.setattr("trajectorylock.imagery.fetch_url", _http(200, JPEG))
    httpd = make_server("127.0.0.1", 0)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    port = httpd.server_address[1]
    case = json.loads(json.dumps(EXAMPLE_CASE))
    case["analysis"] = {"monte_carlo_samples": 200, "random_seed": 23}
    try:
        review_req = urllib.request.Request(
            f"http://127.0.0.1:{port}/api/review",
            data=json.dumps(case).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(review_req, timeout=20) as resp:
            review = json.loads(resp.read().decode("utf-8"))
        assert base64.b64decode(review["imagery"]["image_base64"]) == JPEG
        assert "NASA GIBS" in review["summary"]
        analyze_req = urllib.request.Request(
            f"http://127.0.0.1:{port}/api/analyze",
            data=json.dumps(case).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(analyze_req, timeout=20) as resp:
            analyzed = json.loads(resp.read().decode("utf-8"))
        assert "image_base64" not in analyzed
        assert "imagery" not in analyzed
        assert analyzed["schema_version"] == "trajectorylock-result-0.1"
    finally:
        httpd.shutdown()
        httpd.server_close()
