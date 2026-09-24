"""Worker homepage: one primary Download, focus, footer, system color scheme.

Landing copy stays on what TrajectoryLock does. Download route and counters stay.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = (ROOT / "workers" / "download-tracker" / "src" / "index.js").read_text(
    encoding="utf-8"
)
HTML = INDEX[INDEX.index("<!doctype html>") : INDEX.rindex("</html>") + 7]


def test_primary_download_is_the_hero_link() -> None:
    assert 'id="download"' in HTML
    assert 'href="/download?asset=${DEFAULT_ASSET}"' in HTML
    assert 'class="btn block primary dl"' in HTML
    assert ">Download</a>" in HTML
    href_at = HTML.index('href="/download?asset=${DEFAULT_ASSET}"')
    assert href_at < HTML.index('id="meshStrip"')
    assert href_at < HTML.index('id="install-btn"')


def test_keyboard_focus_and_quiet_footer() -> None:
    assert ":focus-visible" in HTML
    assert "outline: 3px solid var(--focus)" in HTML
    assert "<footer" in HTML
    assert "Apache-2.0" in HTML
    assert "Aziel Eliab" in HTML
    assert "doi:10.5281/zenodo.22258015" in HTML


def test_system_color_scheme_and_mobile_viewport() -> None:
    assert "color-scheme: dark" in HTML
    assert "prefers-color-scheme: light" in HTML
    assert "color-scheme: light" in HTML
    assert 'name="viewport" content="width=device-width, initial-scale=1"' in HTML
    assert "overflow-wrap: anywhere" in HTML
    assert "flex-wrap: wrap" in HTML


def test_counters_mesh_and_brand_stay() -> None:
    assert '<p class="count">' in HTML
    assert ">Views</span>" in HTML
    assert ">Downloads</span>" in HTML
    assert 'id="meshStrip"' in HTML
    assert 'id="meshLiveCount"' in HTML
    assert "FragGate slug=mesh" in HTML
    assert "QNM-BUILD-1.0" in HTML
    assert "No Node Gate" in HTML
    assert (
        '<div class="brandrow"><img class="brandmark" src="/sigil.png" '
        'width="40" height="40" alt="" decoding="async"></div>'
    ) in HTML
    assert "everblooming" not in HTML.lower()
    assert ("GodLock" + ".AZ") not in HTML
    assert "THIS IS NOT" not in HTML
