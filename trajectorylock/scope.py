"""Honest-scope constants. Public identity: Aziel Eliab."""

from __future__ import annotations

__version__ = "0.1.0"
SPEC = "trajectorylock-v0.1"
PAPER_ID = "TL-WP-0.1"
AUTHOR = "Aziel Eliab"
DOI = "https://doi.org/10.5281/zenodo.22258015"
ZENODO = "https://zenodo.org/records/22258015"
PAPER_FILE = "TrajectoryLock_v0.1.pdf"
DEFAULT_PORT = 8874
LOOPBACK = frozenset({"127.0.0.1", "localhost", "::1"})

LIMITATION = (
    "THIS IS: research prototype / auditable geometric test. Compatibility vs declared official line. "
    "Independence groups so copies don't inflate certainty. CLI + local workbench + JSON API. "
    "THIS IS NOT: a certified forensic instrument; substitute for scene reconstruction, medical findings, lab exam; "
    "shooter/intent/guilt/narrative identifier; automatic detection of invisible projectiles; face recognition. "
    "Match probability is P(match | declared model), not P(official account is true). "
    "Synthetic example results must never be represented as real-case findings. "
    "No private case facts. Author: Aziel Eliab."
)

GUARDRAIL = (
    "Scores measure geometric compatibility under declared assumptions. "
    "This is not a certified forensic instrument. "
    "They do not establish intent, identity, shooter, guilt, credibility, or legal truth. "
    "Match probability is P(match | declared model), not P(the official account is true). "
    "Synthetic example results must never be represented as real-case findings."
)

KID_PLAIN = (
    "How close is this line to the claimed line? "
    "Compatibility is closeness. Match chance is whether it fits the frozen tolerances. "
    "How strong is the evidence is about independent sources, not copy-count."
)
