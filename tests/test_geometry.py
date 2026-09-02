import unittest
import numpy as np

from trajectorylock.geometry import acute_angle_deg, line_distance, triangulate_rays


class GeometryTests(unittest.TestCase):
    def test_acute_angle_ignores_polarity(self):
        self.assertAlmostEqual(acute_angle_deg([1, 0, 0], [-1, 0, 0]), 0.0)

    def test_parallel_line_distance(self):
        self.assertAlmostEqual(line_distance([0, 0, 0], [1, 0, 0], [0, 2, 0], [1, 0, 0]), 2.0)

    def test_triangulates_crossing_rays(self):
        result = triangulate_rays([
            {"origin": [0, 0, 0], "direction": [1, 1, 0], "angular_sigma_deg": 0.1},
            {"origin": [2, 0, 0], "direction": [-1, 1, 0], "angular_sigma_deg": 0.1},
        ])
        np.testing.assert_allclose(result.point, [1, 1, 0], atol=1e-8)

    def test_rejects_degenerate_rays(self):
        with self.assertRaisesRegex(ValueError, "degenerate"):
            triangulate_rays([
                {"origin": [0, 0, 0], "direction": [1, 0, 0]},
                {"origin": [0, 1, 0], "direction": [1, 0, 0]},
            ])


if __name__ == "__main__":
    unittest.main()

