"""Numerically stable geometry primitives for trajectory reconstruction."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable

import numpy as np

EPS = 1e-12


def vec3(value, name: str = "vector") -> np.ndarray:
    a = np.asarray(value, dtype=float)
    if a.shape != (3,) or not np.all(np.isfinite(a)):
        raise ValueError(f"{name} must contain exactly three finite numbers")
    return a


def unit(value, name: str = "direction") -> np.ndarray:
    a = vec3(value, name)
    n = float(np.linalg.norm(a))
    if n < EPS:
        raise ValueError(f"{name} cannot be zero")
    return a / n


def acute_angle_deg(a, b) -> float:
    """Unsigned line angle (0..90 degrees); line direction is polarity-free."""
    dot = float(np.clip(abs(np.dot(unit(a), unit(b))), 0.0, 1.0))
    return math.degrees(math.acos(dot))


def line_distance(point_a, direction_a, point_b, direction_b) -> float:
    """Shortest distance between infinite 3D lines."""
    p1, p2 = vec3(point_a), vec3(point_b)
    d1, d2 = unit(direction_a), unit(direction_b)
    cross = np.cross(d1, d2)
    cn = float(np.linalg.norm(cross))
    if cn < 1e-9:
        return float(np.linalg.norm(np.cross(p2 - p1, d1)))
    return abs(float(np.dot(p2 - p1, cross / cn)))


@dataclass(frozen=True)
class ReconstructedPoint:
    point: np.ndarray
    sigma_m: float
    ray_residual_m: float
    condition_number: float
    observation_count: int


def triangulate_rays(rays: Iterable[dict], surveyed_points: Iterable[dict] = ()) -> ReconstructedPoint:
    """Weighted least-squares intersection of 3D rays and surveyed points.

    A sight ray constrains the point perpendicular to its direction. Angular
    uncertainty is converted to a transverse uncertainty using the supplied
    `range_hint_m` (default 10 m). Survey points constrain all axes.
    """
    eye = np.eye(3)
    A = np.zeros((3, 3), dtype=float)
    b = np.zeros(3, dtype=float)
    constraints = []
    count = 0
    for ray in rays:
        o = vec3(ray["origin"], "ray origin")
        d = unit(ray["direction"], "ray direction")
        sigma_deg = max(float(ray.get("angular_sigma_deg", 0.5)), 1e-4)
        range_hint = max(float(ray.get("range_hint_m", 10.0)), 0.1)
        sigma = max(math.tan(math.radians(sigma_deg)) * range_hint, 1e-4)
        w = float(ray.get("weight", 1.0)) / (sigma * sigma)
        P = eye - np.outer(d, d)
        A += w * P
        b += w * (P @ o)
        constraints.append((o, d, w))
        count += 1
    for item in surveyed_points:
        p = vec3(item["point"], "survey point")
        sigma = max(float(item.get("sigma_m", 0.01)), 1e-5)
        w = float(item.get("weight", 1.0)) / (sigma * sigma)
        A += w * eye
        b += w * p
        count += 1
    if count < 2:
        raise ValueError("a feature needs at least two geometric observations")
    condition = float(np.linalg.cond(A))
    if not np.isfinite(condition) or condition > 1e12:
        raise ValueError("feature geometry is degenerate; add a separated viewpoint or survey point")
    point = np.linalg.solve(A, b)
    residuals = [np.linalg.norm(np.cross(point - o, d)) for o, d, _ in constraints]
    residual = float(np.sqrt(np.mean(np.square(residuals)))) if residuals else 0.0
    covariance = np.linalg.inv(A)
    sigma = float(math.sqrt(max(np.trace(covariance) / 3.0, 1e-10)))
    return ReconstructedPoint(point, sigma, residual, condition, count)


@dataclass(frozen=True)
class ReconstructedLine:
    point: np.ndarray
    direction: np.ndarray
    angular_sigma_deg: float
    offset_sigma_m: float
    rms_residual_m: float


def fit_line(points: Iterable[ReconstructedPoint], direct_lines: Iterable[dict] = ()) -> ReconstructedLine:
    pts = list(points)
    lines = list(direct_lines)
    if len(pts) < 2 and not lines:
        raise ValueError("trajectory needs two reconstructed features or one direct line")

    if len(pts) >= 2:
        X = np.vstack([p.point for p in pts])
        weights = np.asarray([1.0 / max(p.sigma_m**2, 1e-8) for p in pts])
        center = np.average(X, axis=0, weights=weights)
        centered = X - center
        cov = (centered * weights[:, None]).T @ centered / weights.sum()
        vals, vectors = np.linalg.eigh(cov)
        direction = vectors[:, int(np.argmax(vals))]
        residuals = np.linalg.norm(np.cross(centered, direction), axis=1)
        rms = float(np.sqrt(np.average(residuals**2, weights=weights)))
        span = max(float(np.ptp(X @ direction)), 1e-3)
        offset_sigma = float(math.sqrt(np.average([p.sigma_m**2 for p in pts], weights=weights)))
        angular_sigma = math.degrees(math.atan2(max(rms, offset_sigma), span))
    else:
        first = lines[0]
        center = vec3(first["point"], "direct line point")
        direction = unit(first["direction"], "direct line direction")
        rms = 0.0
        offset_sigma = float(first.get("offset_sigma_m", 0.05))
        angular_sigma = float(first.get("angular_sigma_deg", 1.0))

    # Blend independent direct-line direction estimates in an orientation-safe way.
    direction_sum = direction / max(angular_sigma, 1e-3) ** 2
    dir_weight = 1.0 / max(angular_sigma, 1e-3) ** 2
    centers = [(center, 1.0 / max(offset_sigma, 1e-4) ** 2)]
    for line in lines:
        d = unit(line["direction"], "direct line direction")
        if np.dot(d, direction) < 0:
            d = -d
        sig_a = max(float(line.get("angular_sigma_deg", 1.0)), 1e-3)
        w = float(line.get("weight", 1.0)) / sig_a**2
        direction_sum += w * d
        dir_weight += w
        sig_o = max(float(line.get("offset_sigma_m", 0.05)), 1e-4)
        centers.append((vec3(line["point"], "direct line point"), float(line.get("weight", 1.0)) / sig_o**2))
    direction = unit(direction_sum / dir_weight)
    center = sum(p * w for p, w in centers) / sum(w for _, w in centers)
    angular_sigma = max(0.05, 1.0 / math.sqrt(dir_weight))
    offset_sigma = max(0.001, 1.0 / math.sqrt(sum(w for _, w in centers)))
    return ReconstructedLine(center, direction, angular_sigma, offset_sigma, rms)


def perturb_direction(direction, sigma_deg: float, rng: np.random.Generator) -> np.ndarray:
    d = unit(direction)
    # Gaussian rotation vector projected perpendicular to d.
    noise = rng.normal(0.0, math.radians(max(sigma_deg, 0.0)), 3)
    noise -= np.dot(noise, d) * d
    return unit(d + noise)

