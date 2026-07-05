#!/usr/bin/env python3
"""Identity primitive for routing-pack dedup (deterministic)."""

import hashlib
import re

_WS = re.compile(r"\s+")
_NONWORD = re.compile(r"[^a-z0-9]+")


def normalize(text):
    text = str(text or "").lower()
    text = _NONWORD.sub(" ", text)
    return _WS.sub(" ", text).strip()


def fingerprint(*parts):
    tokens = sorted({normalize(p) for p in parts if str(p).strip()})
    return hashlib.sha256("|".join(tokens).encode("utf-8")).hexdigest()


def fingerprint_pack(manifest):
    """Fingerprint over source_project + stages + candidate_schema (not the display name)."""
    stages = sorted(str(s) for s in manifest.get("stages", []))
    return fingerprint(manifest.get("source_project", ""),
                       manifest.get("candidate_schema", ""), *stages)
