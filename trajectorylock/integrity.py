"""Evidence hashing and canonical case fingerprints."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


def sha256_file(path: str | Path) -> dict:
    p = Path(path)
    h = hashlib.sha256()
    size = 0
    with p.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
            size += len(chunk)
    return {"path": str(p.resolve()), "size_bytes": size, "sha256": h.hexdigest()}


def canonical_hash(data: dict) -> str:
    encoded = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    return hashlib.sha256(encoded).hexdigest()

