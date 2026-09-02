"""Case validation and end-to-end analysis pipeline."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone

from .geometry import fit_line, triangulate_rays
from .integrity import canonical_hash
from .scoring import compare_lines, evidence_strength, score_witnesses
from .scope import AUTHOR, GUARDRAIL, LIMITATION, SPEC, __version__


def _validate(case: dict) -> None:
    required = ["case_id", "sources", "observations", "official_hypothesis"]
    missing = [name for name in required if name not in case]
    if missing:
        raise ValueError(f"missing required fields: {', '.join(missing)}")
    ids = [s.get("id") for s in case["sources"]]
    if None in ids or len(ids) != len(set(ids)):
        raise ValueError("every source needs a unique id")
    known = set(ids)
    for item in case["observations"]:
        if item.get("source_id") not in known:
            raise ValueError(f"observation references unknown source {item.get('source_id')!r}")


def analyze_case(case: dict, samples: int | None = None, seed: int | None = None) -> dict:
    _validate(case)
    by_feature = defaultdict(lambda: {"rays": [], "points": []})
    direct_lines, witnesses = [], []
    source_map = {s["id"]: s for s in case["sources"]}
    used_sources = set()
    for observation in case["observations"]:
        item = dict(observation)
        source = source_map[item["source_id"]]
        item["weight"] = float(item.get("weight", 1.0)) * float(source.get("quality", 0.5))
        kind = item.get("type")
        if kind == "visual_ray":
            by_feature[item["feature_id"]]["rays"].append(item)
        elif kind == "survey_point":
            by_feature[item["feature_id"]]["points"].append(item)
        elif kind == "direct_line":
            direct_lines.append(item)
        elif kind == "witness_bearing":
            witnesses.append(item)
        else:
            raise ValueError(f"unsupported observation type {kind!r}")
        used_sources.add(item["source_id"])

    features, feature_objects, warnings = {}, [], []
    for feature_id, observations in by_feature.items():
        try:
            result = triangulate_rays(observations["rays"], observations["points"])
        except ValueError as exc:
            warnings.append(f"feature {feature_id}: {exc}")
            continue
        feature_objects.append(result)
        features[feature_id] = {
            "point_m": [round(float(v), 6) for v in result.point],
            "sigma_m": round(result.sigma_m, 6),
            "ray_residual_m": round(result.ray_residual_m, 6),
            "condition_number": round(result.condition_number, 3),
            "observation_count": result.observation_count,
        }
    line = fit_line(feature_objects, direct_lines)
    mc_samples = int(samples if samples is not None else case.get("analysis", {}).get("monte_carlo_samples", 20000))
    if not 100 <= mc_samples <= 1_000_000:
        raise ValueError("monte_carlo_samples must be between 100 and 1,000,000")
    random_seed = int(seed if seed is not None else case.get("analysis", {}).get("random_seed", 7))
    comparison = compare_lines(line, case["official_hypothesis"], mc_samples, random_seed)
    source_confidence = evidence_strength([source_map[s] for s in used_sources], len(feature_objects))
    witness = score_witnesses(witnesses, line.direction)
    result = {
        "schema_version": "trajectorylock-result-0.1",
        "case_id": case["case_id"],
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "input_sha256": canonical_hash(case),
        "trajectory": {
            "point_m": [round(float(v), 6) for v in line.point],
            "direction_unit": [round(float(v), 8) for v in line.direction],
            "angular_sigma_deg": round(line.angular_sigma_deg, 4),
            "offset_sigma_m": round(line.offset_sigma_m, 6),
            "fit_rms_residual_m": round(line.rms_residual_m, 6),
        },
        "reconstructed_features": features,
        "official_narrative_comparison": comparison,
        "reconstruction_confidence": source_confidence,
        "witness_corroboration": witness,
        "warnings": warnings,
        "interpretation": {
            "primary_statement": comparison["conclusion"],
            "guardrail": GUARDRAIL,
            "limitation": LIMITATION,
            "certified_instrument": False,
            "author": AUTHOR,
            "product_version": __version__,
            "spec": SPEC,
        },
        "frozen_tolerances": comparison["declared_tolerances"],
    }
    result["result_sha256"] = canonical_hash(result)
    return result

