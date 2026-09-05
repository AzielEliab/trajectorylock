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


FULL_AI_CLIENTS = (
    "ChatGPT (GPT Actions / OpenAI)",
    "Grok (xAI)",
    "Venice",
    "Claude (Anthropic)",
    "Cursor (MCP)",
    "Glama (MCP)",
    "Perplexity",
    "Microsoft Copilot / Bing",
    "Google Gemini / Vertex",
    "Mistral",
    "Meta AI",
    "Apple Intelligence",
    "Amazon Q",
    "DuckAssist",
    "You.com",
    "Cohere",
    "MCP/OpenAPI-capable assistants",
)


def test_readme_three_steps() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "## Three steps" in readme
    assert "Load example" in readme
    assert "Run check" in readme
    assert "Import" in readme
    assert "10.5281/zenodo.22258015" in readme
    assert "never stores media" in readme.lower()
    assert "certified forensic instrument" in readme.lower()
    assert "Aziel Eliab" in readme
    assert ("GodLock" + ".AZ") not in readme


def test_readme_and_skill_list_full_ai_clients() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    runtime = (ROOT / "workers" / "download-tracker" / "src" / "runtime.js").read_text(
        encoding="utf-8"
    )
    assert "## Use with AI clients" in readme
    assert "## Use with Grok / ChatGPT / Venice" not in readme
    assert "## Use with AI clients" in SKILL
    for name in FULL_AI_CLIENTS:
        assert name in readme
        assert name in SKILL
        assert name in runtime
