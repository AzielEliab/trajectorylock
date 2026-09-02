"""Uncertainty propagation, source independence, and narrative comparison."""

from __future__ import annotations

import math
from collections import defaultdict

import numpy as np

from .geometry import acute_angle_deg, line_distance, perturb_direction, unit, vec3


def evidence_strength(sources: list[dict], reconstructed_features: int) -> dict:
    """Return a bounded confidence estimate without double-counting copies."""
    groups: dict[str, list[float]] = defaultdict(list)
    calibrated = 0
    for source in sources:
        q = min(1.0, max(0.0, float(source.get("quality", 0.5))))
        r = min(1.0, max(0.0, float(source.get("reliability", 1.0))))
        groups[str(source.get("independence_group", source.get("id", "unknown")))].append(q * r)
        calibrated += bool(source.get("calibrated", False))
    # Within a group, the best item counts fully and copies add at most 20% total.
    effective = 0.0
    for values in groups.values():
        values.sort(reverse=True)
        effective += values[0] + 0.2 * (1.0 - math.exp(-sum(values[1:])))
    independent_groups = len(groups)
    source_term = 1.0 - math.exp(-effective / 2.2)
    geometry_term = min(1.0, reconstructed_features / 3.0)
    calibration_term = calibrated / len(sources) if sources else 0.0
    confidence = 100.0 * (0.55 * source_term + 0.30 * geometry_term + 0.15 * calibration_term)
    return {
        "confidence_percent": round(min(confidence, 99.0), 2),
        "effective_source_count": round(effective, 3),
        "independent_group_count": independent_groups,
        "calibrated_source_fraction": round(calibration_term, 3),
    }


def compare_lines(reconstructed, official: dict, samples: int = 20000, seed: int = 7) -> dict:
    op = vec3(official["point"], "official point")
    od = unit(official["direction"], "official direction")
    os_a = max(float(official.get("angular_sigma_deg", 1.0)), 0.01)
    os_o = max(float(official.get("offset_sigma_m", 0.10)), 0.001)
    tolerance_a = max(float(official.get("angle_tolerance_deg", 3.0)), 0.01)
    tolerance_o = max(float(official.get("offset_tolerance_m", 0.30)), 0.001)

    measured_angle = acute_angle_deg(reconstructed.direction, od)
    measured_offset = line_distance(reconstructed.point, reconstructed.direction, op, od)
    rng = np.random.default_rng(seed)
    matches = 0
    likelihood_sum = 0.0
    angles = np.empty(samples)
    offsets = np.empty(samples)
    combined_a = math.hypot(reconstructed.angular_sigma_deg, os_a)
    combined_o = math.hypot(reconstructed.offset_sigma_m, os_o)
    for i in range(samples):
        rd = perturb_direction(reconstructed.direction, reconstructed.angular_sigma_deg, rng)
        o_dir = perturb_direction(od, os_a, rng)
        rp = reconstructed.point + rng.normal(0.0, reconstructed.offset_sigma_m, 3)
        o_point = op + rng.normal(0.0, os_o, 3)
        angle = acute_angle_deg(rd, o_dir)
        offset = line_distance(rp, rd, o_point, o_dir)
        angles[i], offsets[i] = angle, offset
        matches += angle <= tolerance_a and offset <= tolerance_o
        likelihood_sum += math.exp(-0.5 * ((angle / max(combined_a, tolerance_a)) ** 2 + (offset / max(combined_o, tolerance_o)) ** 2))
    threshold_probability = 100.0 * matches / samples
    compatibility = 100.0 * likelihood_sum / samples
    if threshold_probability >= 80:
        conclusion = "consistent_with_declared_tolerances"
    elif threshold_probability <= 20:
        conclusion = "inconsistent_with_declared_tolerances"
    else:
        conclusion = "indeterminate"
    return {
        "measured_angle_difference_deg": round(measured_angle, 4),
        "measured_line_offset_m": round(measured_offset, 4),
        "compatibility_score_percent": round(compatibility, 2),
        "threshold_match_probability_percent": round(threshold_probability, 2),
        "conclusion": conclusion,
        "angle_95_interval_deg": [round(float(np.quantile(angles, 0.025)), 4), round(float(np.quantile(angles, 0.975)), 4)],
        "offset_95_interval_m": [round(float(np.quantile(offsets, 0.025)), 4), round(float(np.quantile(offsets, 0.975)), 4)],
        "monte_carlo_samples": samples,
        "random_seed": seed,
        "declared_tolerances": {"angle_deg": tolerance_a, "offset_m": tolerance_o},
    }


def score_witnesses(witnesses: list[dict], trajectory_direction) -> dict:
    if not witnesses:
        return {"count": 0, "weighted_agreement_percent": None, "details": []}
    details, total_w, total = [], 0.0, 0.0
    for witness in witnesses:
        delta = acute_angle_deg(witness["direction"], trajectory_direction)
        sigma = max(float(witness.get("angular_sigma_deg", 15.0)), 1.0)
        reliability = min(1.0, max(0.0, float(witness.get("reliability", 0.5))))
        agreement = math.exp(-0.5 * (delta / sigma) ** 2)
        total += agreement * reliability
        total_w += reliability
        details.append({"source_id": witness.get("source_id"), "angle_difference_deg": round(delta, 3), "agreement_percent": round(100 * agreement, 2), "reliability_weight": reliability})
    return {"count": len(witnesses), "weighted_agreement_percent": round(100 * total / total_w, 2) if total_w else None, "details": details}

