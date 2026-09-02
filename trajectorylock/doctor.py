"""Self-check for TrajectoryLock. No network, no telemetry."""

from __future__ import annotations

import copy
import json
from typing import Callable

from trajectorylock import __version__
from trajectorylock.example import EXAMPLE_CASE
from trajectorylock.geometry import acute_angle_deg, line_distance, triangulate_rays
from trajectorylock.pipeline import analyze_case
from trajectorylock.scoring import evidence_strength
from trajectorylock.scope import AUTHOR, GUARDRAIL, LIMITATION, LOOPBACK, SPEC
from trajectorylock.server import make_server

Check = tuple[str, bool, str]


def _ok(name: str, detail: str = "") -> Check:
    return name, True, detail


def _fail(name: str, detail: str) -> Check:
    return name, False, detail


def _check_version() -> Check:
    if __version__ == "0.1.0" and SPEC == "trajectorylock-v0.1":
        return _ok("version", f"{__version__} {SPEC}")
    return _fail("version", f"{__version__} {SPEC}")


def _check_identity() -> Check:
    if AUTHOR != "Aziel Eliab":
        return _fail("identity", AUTHOR)
    blob = LIMITATION + GUARDRAIL + AUTHOR
    if ("GodLock" + ".AZ") in blob:
        return _fail("identity", "forbidden identity label leaked")
    return _ok("identity", AUTHOR)


def _check_guardrail() -> Check:
    g = GUARDRAIL.lower()
    needed = (
        "not a certified forensic instrument",
        "p(match | declared model)",
        "shooter",
        "synthetic example",
    )
    missing = [n for n in needed if n not in g]
    if missing:
        return _fail("guardrail", f"missing {missing}")
    if "this is not a certified forensic instrument" not in LIMITATION.lower():
        if "not: a certified forensic instrument" not in LIMITATION.lower():
            return _fail("limitation", "missing certified-instrument refusal")
    return _ok("guardrail", "refuses overclaim")


def _check_geometry() -> Check:
    if abs(acute_angle_deg([1, 0, 0], [-1, 0, 0])) > 1e-9:
        return _fail("acute angle", "polarity not ignored")
    dist = line_distance([0, 0, 0], [1, 0, 0], [0, 2, 0], [1, 0, 0])
    if abs(dist - 2.0) > 1e-9:
        return _fail("line distance", str(dist))
    point = triangulate_rays(
        [
            {"origin": [0, 0, 0], "direction": [1, 1, 0], "angular_sigma_deg": 0.1},
            {"origin": [2, 0, 0], "direction": [-1, 1, 0], "angular_sigma_deg": 0.1},
        ]
    )
    if abs(float(point.point[0]) - 1.0) > 1e-6 or abs(float(point.point[1]) - 1.0) > 1e-6:
        return _fail("triangulate", str(point.point))
    return _ok("geometry", "angle/offset/rays")


def _check_independence() -> Check:
    base = [{"id": "a", "quality": 0.9, "reliability": 1, "calibrated": True, "independence_group": "g"}]
    copied = base + [
        {"id": f"copy{i}", "quality": 0.9, "reliability": 1, "calibrated": True, "independence_group": "g"}
        for i in range(20)
    ]
    a = evidence_strength(base, 2)["effective_source_count"]
    b = evidence_strength(copied, 2)["effective_source_count"]
    if (b - a) >= 0.21:
        return _fail("independence", f"copies inflated {a} -> {b}")
    return _ok("independence", f"delta {round(b - a, 4)}")


def _check_demo() -> Check:
    case = copy.deepcopy(EXAMPLE_CASE)
    case["analysis"]["monte_carlo_samples"] = 400
    result = analyze_case(case)
    g = result["interpretation"]["guardrail"]
    if "not a certified forensic instrument" not in g.lower():
        return _fail("demo guardrail", g[:80])
    if result["interpretation"]["certified_instrument"] is not False:
        return _fail("certified flag", str(result["interpretation"]["certified_instrument"]))
    if result["official_narrative_comparison"]["conclusion"] != "consistent_with_declared_tolerances":
        return _fail("demo conclusion", result["official_narrative_comparison"]["conclusion"])
    return _ok("demo", result["case_id"])


def _check_loopback() -> Check:
    try:
        make_server("0.0.0.0", 9)
    except ValueError as exc:
        if "loopback" in str(exc).lower() and "127.0.0.1" in LOOPBACK:
            return _ok("loopback", "rejects 0.0.0.0")
        return _fail("loopback", str(exc))
    return _fail("loopback", "accepted 0.0.0.0")


CHECKS: tuple[Callable[[], Check], ...] = (
    _check_version,
    _check_identity,
    _check_guardrail,
    _check_geometry,
    _check_independence,
    _check_demo,
    _check_loopback,
)


def run_doctor(*, as_json: bool = False) -> int:
    results = []
    failed = 0
    for fn in CHECKS:
        name, ok, detail = fn()
        results.append({"name": name, "ok": ok, "detail": detail})
        if not ok:
            failed += 1
        mark = "ok" if ok else "FAIL"
        if not as_json:
            print(f"[{mark}] {name}" + (f" — {detail}" if detail else ""))
    payload = {
        "ok": failed == 0,
        "failed": failed,
        "checks": results,
        "version": __version__,
        "spec": SPEC,
        "limitation": LIMITATION,
        "guardrail": GUARDRAIL,
        "certified_instrument": False,
        "author": AUTHOR,
        "network": False,
        "telemetry": False,
    }
    if as_json:
        print(json.dumps(payload, indent=2))
    else:
        print("limitation:", LIMITATION)
        print("doctor", "passed" if failed == 0 else "failed")
    return 0 if failed == 0 else 1
