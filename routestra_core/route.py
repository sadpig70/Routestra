#!/usr/bin/env python3
"""Routing — select the best eligible candidate for a demand.

Generalizes SkyGrid.plan_compute_roaming: score every candidate, pick the highest-score
eligible one (deterministic tie-break by name), record rejection reasons. Pure stdlib.
"""

from .candidate import validate_pool


def route(demand, candidates, score_fn, now="", required=("name",)):
    """score_fn(candidate) -> ScoreResult (dict with name/score/eligible/verified/reason)."""
    pv = validate_pool(candidates, required)
    if not pv["ok"]:
        raise ValueError(f"invalid candidate pool: {pv['reason']}")
    scored = [score_fn(c) for c in candidates]
    eligible = [s for s in scored if s["eligible"]]
    best = min(eligible, key=lambda s: (-s["score"], str(s["name"]))) if eligible else None
    selected_evidence = None
    if best is not None:
        cand = next((c for c in candidates if c.get("name") == best["name"]), {})
        selected_evidence = cand.get("evidence_hash")
    return {
        "selected": best["name"] if best else None,
        "selected_score": best["score"] if best else 0.0,
        "selected_evidence": selected_evidence,
        "all_scores": scored,
        "demand": demand,
        "routed_at": now,
    }
