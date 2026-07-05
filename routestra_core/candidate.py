#!/usr/bin/env python3
"""Candidate / telemetry model + validation.

A candidate is a public resource-source record: {name, ...attributes, [evidence_hash]}.
Validation guarantees the fields scoring/routing rely on.
"""


def _is_number(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def validate_candidate(candidate, required=()):
    """Return {ok, reason}. Deterministic; no clock/network/AI."""
    if not isinstance(candidate, dict) or "name" not in candidate:
        return {"ok": False, "reason": "candidate_missing_name"}
    for field in required:
        if field not in candidate:
            return {"ok": False, "reason": f"missing:{field}"}
    return {"ok": True, "reason": ""}


def validate_pool(candidates, required=()):
    if not isinstance(candidates, list):
        return {"ok": False, "reason": "pool_not_list"}
    seen = set()
    for c in candidates:
        cv = validate_candidate(c, required)
        if not cv["ok"]:
            return cv
        if c["name"] in seen:
            return {"ok": False, "reason": f"duplicate_candidate:{c['name']}"}
        seen.add(c["name"])
    return {"ok": True, "reason": ""}
