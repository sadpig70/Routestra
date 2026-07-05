#!/usr/bin/env python3
"""Threshold-bounded verdict — merge dimension verdicts by severity.

Generalizes ThermalCascadeBound.evaluate_site: each dimension (power, thermal, ...) is
judged compliant/restricted/violation vs its threshold; the site verdict is the highest
severity. Pure stdlib.
"""

from .verdict import SEVERITY


def compliant(dimension, reason="within threshold"):
    return {"dimension": dimension, "verdict": "compliant", "reason": reason}


def restricted(dimension, reason):
    return {"dimension": dimension, "verdict": "restricted", "reason": reason}


def violation(dimension, reason):
    return {"dimension": dimension, "verdict": "violation", "reason": reason}


def bound(dimensions):
    """Merge dimension verdicts to the highest severity (violation > restricted > compliant)."""
    if not dimensions:
        return {"verdict": "restricted", "reason": "no_dimensions", "worst": None, "dimensions": []}
    worst = max(dimensions, key=lambda d: SEVERITY[d["verdict"]])
    return {"verdict": worst["verdict"], "reason": worst["reason"],
            "worst": worst["dimension"], "dimensions": dimensions}
