"""Public identity is Aziel Eliab only. Forbidden GodLock-plus-AZ identity label."""

from pathlib import Path

from trajectorylock.scope import AUTHOR, LIMITATION

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN = "GodLock" + ".AZ"


def _iter_text_files():
    skip = {".git", ".venv", "__pycache__", "dist", ".pytest_cache", "node_modules", ".wrangler", "tests"}
    for path in ROOT.rglob("*"):
        if any(part in skip for part in path.parts):
            continue
        if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".pdf", ".gz", ".zip", ".pyc"}:
            continue
        if path.is_file():
            yield path


def test_author_is_aziel_eliab() -> None:
    assert AUTHOR == "Aziel Eliab"
    assert FORBIDDEN not in LIMITATION


def test_tree_has_no_godlock_az_label() -> None:
    hits = []
    for path in _iter_text_files():
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if FORBIDDEN in text:
            hits.append(str(path.relative_to(ROOT)))
    assert hits == []
