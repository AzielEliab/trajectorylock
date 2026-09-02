import copy
import unittest

from trajectorylock.example import EXAMPLE_CASE
from trajectorylock.pipeline import analyze_case
from trajectorylock.scoring import evidence_strength


class PipelineTests(unittest.TestCase):
    def test_demo_matches(self):
        case = copy.deepcopy(EXAMPLE_CASE)
        case["analysis"]["monte_carlo_samples"] = 1000
        result = analyze_case(case)
        self.assertEqual(result["official_narrative_comparison"]["conclusion"], "consistent_with_declared_tolerances")
        self.assertGreater(result["official_narrative_comparison"]["threshold_match_probability_percent"], 80)
        self.assertEqual(len(result["result_sha256"]), 64)

    def test_bad_official_direction_is_inconsistent(self):
        case = copy.deepcopy(EXAMPLE_CASE)
        case["official_hypothesis"]["direction"] = [0, 1, 0]
        case["analysis"]["monte_carlo_samples"] = 1000
        result = analyze_case(case)
        self.assertEqual(result["official_narrative_comparison"]["conclusion"], "inconsistent_with_declared_tolerances")

    def test_correlated_copy_has_small_effect(self):
        base = [{"id": "a", "quality": .9, "reliability": 1, "calibrated": True, "independence_group": "g"}]
        copied = base + [{"id": f"copy{i}", "quality": .9, "reliability": 1, "calibrated": True, "independence_group": "g"} for i in range(20)]
        a = evidence_strength(base, 2)["effective_source_count"]
        b = evidence_strength(copied, 2)["effective_source_count"]
        self.assertLess(b - a, 0.21)


if __name__ == "__main__":
    unittest.main()

