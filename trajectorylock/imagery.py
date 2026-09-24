"""Satellite frame for an event place and time.

Source: NASA Global Imagery Browse Services (GIBS), no API key.
Layer: MODIS Terra Corrected Reflectance (true color), daily composite.

Tile URL (EPSG:3857, Google Maps compatible, 256-pixel tiles)::

    https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Terra_CorrectedReflectance_TrueColor/default/{YYYY-MM-DD}/GoogleMapsCompatible_Level9/{z}/{y}/{x}.jpg

A place name with no coordinates is resolved through OpenStreetMap Nominatim.
The bytes shown are the bytes GIBS returned. This module does not draw a stand-in image.

Author: Aziel Eliab.
"""

from __future__ import annotations

import base64
import hashlib
import json
import math
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from typing import Callable

from .pipeline import analyze_case

SOURCE = "NASA GIBS"
PRODUCT = "MODIS_Terra_CorrectedReflectance_TrueColor"
PRODUCT_TITLE = "MODIS Terra corrected reflectance (true color)"
GEOCODE_SOURCE = "OpenStreetMap Nominatim"
USER_AGENT = "TrajectoryLock/0.1 (local research workbench; Aziel Eliab)"
TILE_SIZE = 256
ZOOM = 8
SEARCH_DAYS = 7
FETCH_TIMEOUT = 12.0
GIBS_TEMPLATE = (
    "https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/"
    f"{PRODUCT}/default/{{date}}/GoogleMapsCompatible_Level9/{{z}}/{{y}}/{{x}}.jpg"
)
NOMINATIM = "https://nominatim.openstreetmap.org/search"

Fetch = Callable[[str, float], tuple[int, str, bytes]]


def fetch_url(url: str, timeout: float = FETCH_TIMEOUT) -> tuple[int, str, bytes]:
    """GET url. Returns status, content-type, and body. HTTP errors return the status."""
    request = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "image/jpeg, application/json;q=0.9, */*;q=0.1"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, response.headers.get("Content-Type", ""), response.read(2_000_000)
    except urllib.error.HTTPError as exc:
        body = exc.read(16_000)
        return exc.code, exc.headers.get("Content-Type", "") if exc.headers else "", body
    except urllib.error.URLError as exc:
        raise ConnectionError(str(exc.reason)) from exc


def _is_jpeg(body: bytes) -> bool:
    return len(body) >= 4 and body[0:3] == b"\xff\xd8\xff"


def _parse_time(value: str) -> datetime:
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _human_span(seconds: float) -> str:
    remaining = int(abs(seconds))
    days, remaining = divmod(remaining, 86400)
    hours, remaining = divmod(remaining, 3600)
    minutes = remaining // 60
    parts: list[str] = []
    if days:
        parts.append(f"{days} day" if days == 1 else f"{days} days")
    if hours:
        parts.append(f"{hours} hour" if hours == 1 else f"{hours} hours")
    if minutes or not parts:
        parts.append(f"{minutes} minute" if minutes == 1 else f"{minutes} minutes")
    return " ".join(parts)


def _tile_address(latitude: float, longitude: float, zoom: int = ZOOM) -> dict:
    span = 2.0 ** zoom
    x_float = (longitude + 180.0) / 360.0 * span
    latitude_rad = math.radians(latitude)
    y_float = (1.0 - math.asinh(math.tan(latitude_rad)) / math.pi) / 2.0 * span
    x_tile = max(0, min(int(span) - 1, int(math.floor(x_float))))
    y_tile = max(0, min(int(span) - 1, int(math.floor(y_float))))
    pixel_x = min(TILE_SIZE - 1, max(0, int((x_float - x_tile) * TILE_SIZE)))
    pixel_y = min(TILE_SIZE - 1, max(0, int((y_float - y_tile) * TILE_SIZE)))
    return {"z": zoom, "x": x_tile, "y": y_tile, "pixel_x": pixel_x, "pixel_y": pixel_y, "tile_size": TILE_SIZE}


def _candidate_dates(when: datetime, radius: int) -> list[datetime]:
    day = when.astimezone(timezone.utc).date()
    dates = [day]
    for step in range(1, radius + 1):
        dates.append(day + timedelta(days=step))
        dates.append(day - timedelta(days=step))
    return dates


def _blank(*, summary: str, next_step: str, relation: str, **extra) -> dict:
    payload = {
        "ok": False,
        "attempted": True,
        "source": SOURCE,
        "product": PRODUCT,
        "product_title": PRODUCT_TITLE,
        "relation": relation,
        "requested_time": None,
        "frame_time": None,
        "time_delta_seconds": None,
        "latitude": None,
        "longitude": None,
        "place": None,
        "geocode_source": None,
        "tile": None,
        "image_media_type": None,
        "image_sha256": None,
        "image_base64": None,
        "source_url": None,
        "summary": summary,
        "next_step": next_step,
    }
    payload.update(extra)
    return payload


def _event_block(case: dict) -> dict:
    event = case.get("event") if isinstance(case, dict) else None
    return event if isinstance(event, dict) else {}


def geocode_place(place: str, *, fetch: Fetch | None = None) -> tuple[float, float]:
    """Resolve a place name. Raises ValueError with a next step when Nominatim has no point."""
    getter = fetch or fetch_url
    query = urllib.parse.urlencode({"q": place, "format": "jsonv2", "limit": "1"})
    try:
        status, _content_type, body = getter(f"{NOMINATIM}?{query}", FETCH_TIMEOUT)
    except ConnectionError as exc:
        raise ValueError(
            f'OpenStreetMap Nominatim did not answer ({exc}). Enter latitude and longitude, then run the check again.'
        ) from exc
    if status != 200:
        raise ValueError(
            f'OpenStreetMap Nominatim returned HTTP {status} for "{place}". Enter latitude and longitude, then run the check again.'
        )
    try:
        rows = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(
            "OpenStreetMap Nominatim returned an unreadable answer. Enter latitude and longitude, then run the check again."
        ) from exc
    if not rows:
        raise ValueError(
            f'No coordinates for "{place}". Enter latitude and longitude, then run the check again.'
        )
    try:
        return float(rows[0]["lat"]), float(rows[0]["lon"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(
            "OpenStreetMap Nominatim returned no usable point. Enter latitude and longitude, then run the check again."
        ) from exc


def pull_imagery(
    *,
    latitude: float | None,
    longitude: float | None,
    when: str | None,
    place: str | None = None,
    fetch: Fetch | None = None,
    search_days: int = SEARCH_DAYS,
) -> dict:
    """Pull one real GIBS tile, or an honest gap with no image bytes."""
    getter = fetch or fetch_url
    label = place.strip() if isinstance(place, str) else ""
    has_lat = latitude is not None and longitude is not None
    has_time = bool(when and str(when).strip())
    if not has_lat and not label and not has_time:
        return {
            "ok": False,
            "attempted": False,
            "source": SOURCE,
            "product": PRODUCT,
            "summary": "",
            "next_step": None,
            "image_base64": None,
            "relation": "not_requested",
        }
    if not has_time:
        return _blank(
            relation="not_requested",
            place=label or None,
            summary="Event time is missing, so no satellite frame was pulled.",
            next_step="Add an event time (UTC, for example 2024-08-15T18:30:00Z), then press Run check.",
        )
    try:
        event_time = _parse_time(str(when))
    except ValueError:
        return _blank(
            relation="not_requested",
            place=label or None,
            requested_time=str(when),
            summary=f'"{when}" is not a time this check can read.',
            next_step="Use a UTC time such as 2024-08-15T18:30:00Z, then press Run check.",
        )

    geocode_source = None
    if not has_lat:
        if not label:
            return _blank(
                relation="not_requested",
                requested_time=event_time.isoformat(),
                summary="No latitude and longitude, so no satellite frame was pulled.",
                next_step="Enter a place, or latitude and longitude, then press Run check.",
            )
        try:
            latitude, longitude = geocode_place(label, fetch=getter)
        except ValueError as exc:
            return _blank(
                relation="unavailable",
                place=label,
                requested_time=event_time.isoformat(),
                summary=str(exc),
                next_step="Enter latitude and longitude, then press Run check.",
            )
        geocode_source = GEOCODE_SOURCE
    assert latitude is not None and longitude is not None
    if not (-90.0 <= float(latitude) <= 90.0 and -180.0 <= float(longitude) <= 180.0):
        return _blank(
            relation="not_requested",
            place=label or None,
            requested_time=event_time.isoformat(),
            summary="Latitude must be between -90 and 90, and longitude between -180 and 180.",
            next_step="Correct the coordinates, then press Run check.",
        )
    latitude = float(latitude)
    longitude = float(longitude)
    tile = _tile_address(latitude, longitude)
    event_day = event_time.date()
    tried_event_day = False
    try:
        for frame_day in _candidate_dates(event_time, search_days):
            url = GIBS_TEMPLATE.format(date=frame_day.isoformat(), z=tile["z"], y=tile["y"], x=tile["x"])
            if frame_day == event_day:
                tried_event_day = True
            status, _content_type, body = getter(url, FETCH_TIMEOUT)
            if status == 200 and _is_jpeg(body):
                return _frame_record(
                    body=body,
                    url=url,
                    tile=tile,
                    event_time=event_time,
                    frame_day=frame_day,
                    latitude=latitude,
                    longitude=longitude,
                    place=label or None,
                    geocode_source=geocode_source,
                    event_day_missing=frame_day != event_day and tried_event_day,
                )
        return _blank(
            relation="missing",
            place=label or None,
            geocode_source=geocode_source,
            latitude=latitude,
            longitude=longitude,
            requested_time=event_time.isoformat(),
            tile=tile,
            summary=(
                f"{SOURCE} had no {PRODUCT_TITLE} frame within {search_days} days of {event_day.isoformat()}. "
                "No image is shown."
            ),
            next_step="Try a different event time, or check that this computer can reach gibs.earthdata.nasa.gov.",
        )
    except ConnectionError as exc:
        return _blank(
            relation="unavailable",
            place=label or None,
            geocode_source=geocode_source,
            latitude=latitude,
            longitude=longitude,
            requested_time=event_time.isoformat(),
            tile=tile,
            summary=f"{SOURCE} did not answer ({exc}). No image is shown.",
            next_step="Check that this computer can reach gibs.earthdata.nasa.gov, then press Run check.",
        )


def _frame_record(
    *,
    body: bytes,
    url: str,
    tile: dict,
    event_time: datetime,
    frame_day,
    latitude: float,
    longitude: float,
    place: str | None,
    geocode_source: str | None,
    event_day_missing: bool,
) -> dict:
    frame_start = datetime(frame_day.year, frame_day.month, frame_day.day, tzinfo=timezone.utc)
    delta_seconds = int((frame_start - event_time).total_seconds())
    same_day = frame_day == event_time.date()
    where = f"{latitude:.6f}, {longitude:.6f}"
    if place:
        where = f"{place} ({where})"
    if same_day:
        relation = "same_calendar_day"
        summary = (
            f"{SOURCE} {PRODUCT_TITLE} for {frame_day.isoformat()} (UTC day), at {where}. "
            f"Daily composite, not a photograph at the event minute. "
            f"Event time {event_time.isoformat()} is {_human_span(delta_seconds)} after 00:00 UTC that day."
        )
    else:
        relation = "nearest"
        direction = "after" if delta_seconds > 0 else "before"
        summary = (
            f"{SOURCE} had no frame for {event_time.date().isoformat()}. "
            f"Nearest frame is {frame_day.isoformat()}, {_human_span(delta_seconds)} {direction} the event time "
            f"({event_time.isoformat()}), at {where}. "
            "Daily composite, not a photograph at the event minute."
        )
    if geocode_source:
        summary += f" Coordinates from {geocode_source}."
    digest = hashlib.sha256(body).hexdigest()
    return {
        "ok": True,
        "attempted": True,
        "source": SOURCE,
        "product": PRODUCT,
        "product_title": PRODUCT_TITLE,
        "relation": relation,
        "requested_time": event_time.isoformat(),
        "frame_time": frame_day.isoformat(),
        "time_delta_seconds": delta_seconds,
        "event_day_missing": event_day_missing,
        "latitude": latitude,
        "longitude": longitude,
        "place": place,
        "geocode_source": geocode_source,
        "tile": tile,
        "image_media_type": "image/jpeg",
        "image_sha256": digest,
        "image_base64": base64.b64encode(body).decode("ascii"),
        "source_url": url,
        "summary": summary,
        "next_step": None,
    }


def pull_for_case(case: dict, *, fetch: Fetch | None = None) -> dict:
    event = _event_block(case)
    latitude = event.get("latitude", event.get("lat"))
    longitude = event.get("longitude", event.get("lon"))
    try:
        if latitude is not None and latitude != "":
            latitude = float(latitude)
        else:
            latitude = None
        if longitude is not None and longitude != "":
            longitude = float(longitude)
        else:
            longitude = None
    except (TypeError, ValueError):
        return _blank(
            relation="not_requested",
            place=(event.get("place") or None),
            requested_time=event.get("time") or event.get("timestamp"),
            summary="Latitude and longitude need to be numbers.",
            next_step="Enter decimal degrees, then press Run check.",
        )
    return pull_imagery(
        latitude=latitude,
        longitude=longitude,
        when=event.get("time") or event.get("timestamp"),
        place=event.get("place"),
        fetch=fetch,
    )


def review_summary(result: dict, imagery: dict) -> str:
    """Plain review: frame honesty, then the line reading, then how the trace is drawn."""
    comparison = result.get("official_narrative_comparison") or {}
    confidence = result.get("reconstruction_confidence") or {}
    lines: list[str] = []
    if imagery.get("attempted"):
        lines.append(imagery.get("summary") or "No satellite summary.")
        if imagery.get("next_step"):
            lines.append(imagery["next_step"])
    else:
        lines.append("No place and time were set, so no satellite frame was pulled.")
        lines.append("Add latitude, longitude, and an event time, then press Run check.")
    lines.append("")
    lines.append(f"Case {result.get('case_id', '?')}.")
    conclusion = comparison.get("conclusion") or ""
    readings = {
        "consistent_with_declared_tolerances": "The measured line fits the declared tolerances.",
        "inconsistent_with_declared_tolerances": "The measured line does not fit the declared tolerances.",
        "indeterminate": "The measured line sits in between the declared tolerances.",
    }
    lines.append(readings.get(conclusion, conclusion or "No line reading."))
    lines.append(
        "Compatibility "
        f"{comparison.get('compatibility_score_percent', '—')}%. "
        "Match chance "
        f"{comparison.get('threshold_match_probability_percent', '—')}% "
        "(P(match | declared model)). "
        "Evidence strength "
        f"{confidence.get('confidence_percent', '—')}%."
    )
    lines.append(
        f"Angle difference {comparison.get('measured_angle_difference_deg', '—')} deg. "
        f"Line offset {comparison.get('measured_line_offset_m', '—')} m."
    )
    lines.append(
        "The line trace is the measured direction and the claimed direction in case coordinates. "
        "It is drawn beside the satellite frame, not surveyed onto the pixels."
    )
    if str(result.get("case_id", "")).startswith("SYNTHETIC"):
        lines.append("Synthetic example. The frame is real imagery of the declared point. The line is not a real case.")
    return "\n".join(lines)


def review_case(case: dict, *, fetch: Fetch | None = None) -> dict:
    """Geometry result (unchanged shape) plus a separate imagery record."""
    result = analyze_case(case)
    imagery = pull_for_case(case, fetch=fetch)
    return {
        "result": result,
        "imagery": imagery,
        "summary": review_summary(result, imagery),
    }
