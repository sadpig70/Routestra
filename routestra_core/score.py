#!/usr/bin/env python3
"""Candidate scoring — value + eligibility (thresholds + evidence).

Generalizes SkyGrid.evaluate_power_availability: a domain `score_fn(candidate)` produces
the value; the kernel applies deterministic thresholds and an evidence check to decide
eligibility. Pure stdlib. Packs may also build a ScoreResult directly.

thresholds: {field: {"min": x} | {"max": y} | {"eq": v}}
evidence_field: name of a candidate field that must be truthy (e.g. "confirmed_renewable").
"""


def eligible_score(name, value):
    return {"name": name, "score": value, "eligible": True, "verified": True, "reason": ""}


def ineligible(name, value, reason, verified=True):
    return {"name": name, "score": value, "eligible": False, "verified": verified, "reason": reason}


def check_thresholds(candidate, thresholds):
    """Return (met, reason). Deterministic scan in sorted field order."""
    for field in sorted(thresholds):
        rule = thresholds[field]
        val = candidate.get(field)
        if "min" in rule and (val is None or val < rule["min"]):
            return False, f"{field}_below_min"
        if "max" in rule and (val is None or val > rule["max"]):
            return False, f"{field}_above_max"
        if "eq" in rule and val != rule["eq"]:
            return False, f"{field}_ne"
    return True, ""


def score(candidate, score_fn, thresholds=None, evidence_field=None):
    """Score one candidate: value from score_fn, eligibility from thresholds + evidence."""
    name = candidate.get("name", "")
    value = score_fn(candidate)
    if evidence_field is not None and not candidate.get(evidence_field):
        return ineligible(name, value, "evidence_not_verified", verified=False)
    met, reason = check_thresholds(candidate, thresholds or {})
    if not met:
        return ineligible(name, value, reason)
    return eligible_score(name, value)
