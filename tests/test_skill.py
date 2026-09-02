from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = (ROOT / "SKILL.md").read_text(encoding="utf-8")


def test_skill_frontmatter_and_urls() -> None:
    assert SKILL.startswith("---\n")
    assert "name: TrajectoryLock" in SKILL
    assert "Mozilla/5.0" in SKILL
    assert "https://trajectorylock-download-tracker.vibelock.workers.dev/openapi.json" in SKILL
    assert "https://aziel-runtime.vibelock.workers.dev/openapi.json" in SKILL
    assert "https://aziel-runtime.vibelock.workers.dev/mcp" in SKILL
    assert "certified forensic instrument" in SKILL.lower()
    assert ("GodLock" + ".AZ") not in SKILL
    assert "10.5281/zenodo.22258015" in SKILL
    assert "/v1/analyze" in SKILL or "/v1/example" in SKILL
