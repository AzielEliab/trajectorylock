"""Refuse overclaim in the guardrail string."""

import copy

from trajectorylock.example import EXAMPLE_CASE
from trajectorylock.pipeline import analyze_case
from trajectorylock.scope import GUARDRAIL, LIMITATION


def test_guardrail_refuses_overclaim() -> None:
    g = GUARDRAIL.lower()
    assert "not a certified forensic instrument" in g
    assert "p(match | declared model)" in g
    assert "shooter" in g
    assert "synthetic example" in g
    assert "intent" in g
    assert "not p(the official account is true)" in g or "not p(official account is true)" in g


def test_limitation_this_is_this_is_not() -> None:
    assert "THIS IS:" in LIMITATION
    assert "THIS IS NOT:" in LIMITATION
    assert "certified forensic instrument" in LIMITATION.lower()
    assert "face recognition" in LIMITATION.lower()
    assert ("GodLock" + ".AZ") not in LIMITATION


def test_analyze_embeds_guardrail() -> None:
    case = copy.deepcopy(EXAMPLE_CASE)
    case["analysis"]["monte_carlo_samples"] = 200
    result = analyze_case(case)
    g = result["interpretation"]["guardrail"]
    assert "not a certified forensic instrument" in g.lower()
    assert result["interpretation"]["certified_instrument"] is False
    assert "P(match | declared model)" in g
