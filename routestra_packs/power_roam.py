#!/usr/bin/env python3
"""PowerRoamMarket — mobile compute roams to the cheapest available power.

source_project: github.com/sadpig70/PowerRoam
stages: route
Binding constraint swapped from grid-lead-time to a communication-latency budget.
"""

from ._base import score as kscore


def _value(c):
    return c["power_available_mw"] / max(c["power_cost"], 1e-9)


def score(candidate, P=None):
    budget = (P or {}).get("demand", {}).get("latency_budget_ms", 1000)
    return kscore(candidate, _value, thresholds={"comm_latency_ms": {"max": budget}})


MANIFEST = {
    "name": "power-roam", "version": "1.0", "stages": ["route"],
    "candidate_schema": "schemas/candidate-roam.schema.json",
    "source_project": "github.com/sadpig70/PowerRoam",
}

SAMPLES = {
    "route": {
        "demand": {"latency_budget_ms": 80},
        "candidates": [
            {"name": "hydro-remote", "power_available_mw": 50, "power_cost": 2.0, "comm_latency_ms": 70},
            {"name": "gas-near", "power_available_mw": 50, "power_cost": 5.0, "comm_latency_ms": 20},
        ],
    },
}
