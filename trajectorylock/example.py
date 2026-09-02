"""A synthetic, internally consistent demonstration case."""

EXAMPLE_CASE = {
    "case_id": "SYNTHETIC-DEMO-001",
    "description": "Synthetic two-camera and survey example; not real evidence.",
    "coordinate_system": "right-handed local metres",
    "sources": [
        {"id": "cam-a", "kind": "video", "quality": 0.90, "reliability": 1.0, "calibrated": True, "independence_group": "camera-a-original"},
        {"id": "cam-b", "kind": "video", "quality": 0.85, "reliability": 1.0, "calibrated": True, "independence_group": "camera-b-original"},
        {"id": "survey-1", "kind": "scene_survey", "quality": 0.98, "reliability": 1.0, "calibrated": True, "independence_group": "survey-team-1"},
        {"id": "witness-1", "kind": "witness", "quality": 0.45, "reliability": 0.6, "calibrated": False, "independence_group": "witness-1"},
    ],
    "observations": [
        {"type": "visual_ray", "source_id": "cam-a", "feature_id": "entry", "origin": [0, -5, 2], "direction": [5, 5, -1], "angular_sigma_deg": 0.25, "range_hint_m": 7.2},
        {"type": "visual_ray", "source_id": "cam-b", "feature_id": "entry", "origin": [10, -5, 2], "direction": [-5, 5, -1], "angular_sigma_deg": 0.25, "range_hint_m": 7.2},
        {"type": "survey_point", "source_id": "survey-1", "feature_id": "entry", "point": [5, 0, 1], "sigma_m": 0.008},
        {"type": "visual_ray", "source_id": "cam-a", "feature_id": "exit", "origin": [0, -5, 2], "direction": [7, 6, -0.6], "angular_sigma_deg": 0.30, "range_hint_m": 9.2},
        {"type": "visual_ray", "source_id": "cam-b", "feature_id": "exit", "origin": [10, -5, 2], "direction": [-3, 6, -0.6], "angular_sigma_deg": 0.30, "range_hint_m": 7.0},
        {"type": "survey_point", "source_id": "survey-1", "feature_id": "exit", "point": [7, 1, 1.4], "sigma_m": 0.008},
        {"type": "witness_bearing", "source_id": "witness-1", "origin": [1, -2, 1.7], "direction": [2, 1, 0.35], "angular_sigma_deg": 12, "reliability": 0.6},
    ],
    "official_hypothesis": {
        "label": "declared official line",
        "point": [5.02, 0.01, 1.01],
        "direction": [2.0, 1.0, 0.4],
        "angular_sigma_deg": 0.8,
        "offset_sigma_m": 0.04,
        "angle_tolerance_deg": 3.0,
        "offset_tolerance_m": 0.25
    },
    "analysis": {"monte_carlo_samples": 12000, "random_seed": 23}
}

