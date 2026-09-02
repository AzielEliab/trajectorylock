"""Independence groups: copies must not inflate certainty."""

from trajectorylock.scoring import evidence_strength


def test_correlated_copies_capped() -> None:
    base = [
        {"id": "a", "quality": 0.9, "reliability": 1, "calibrated": True, "independence_group": "cam-a"}
    ]
    copies = base + [
        {
            "id": f"copy{i}",
            "quality": 0.9,
            "reliability": 1,
            "calibrated": True,
            "independence_group": "cam-a",
        }
        for i in range(50)
    ]
    a = evidence_strength(base, 2)["effective_source_count"]
    b = evidence_strength(copies, 2)["effective_source_count"]
    assert b - a < 0.21


def test_separated_groups_add_more_than_copies() -> None:
    one = [{"id": "a", "quality": 0.9, "reliability": 1, "calibrated": True, "independence_group": "g1"}]
    two = one + [
        {"id": "b", "quality": 0.9, "reliability": 1, "calibrated": True, "independence_group": "g2"}
    ]
    copies = one + [
        {"id": "c", "quality": 0.9, "reliability": 1, "calibrated": True, "independence_group": "g1"}
    ]
    independent = evidence_strength(two, 2)["effective_source_count"]
    correlated = evidence_strength(copies, 2)["effective_source_count"]
    assert independent > correlated
    assert evidence_strength(two, 2)["independent_group_count"] == 2
