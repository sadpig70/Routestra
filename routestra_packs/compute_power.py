#!/usr/bin/env python3
"""ComputePowerPack — reference route pack. Parity with SkyGrid.

source_project: github.com/sadpig70/SkyGrid
stages: route
Parity anchor: score/route must match SkyGrid.evaluate_power_availability /
plan_compute_roaming (availability = grid_capacity * renewable/100 * latency_penalty;
eligible = renewable>=50 AND latency<=demand AND satellite-confirmed).
"""

from ._base import score as kscore


def _availability(c):
    # SkyGrid: grid_capacity_mw * (renewable_pct/100) * max(0, 1 - latency_ms/200)
    return c["grid_capacity_mw"] * (c["renewable_pct"] / 100) * max(0, 1 - c["latency_ms"] / 200)


def score(candidate, P=None):
    """route-stage function (kernel STAGE_FN: route -> score)."""
    max_latency = (P or {}).get("demand", {}).get("max_latency_ms", 200)
    return kscore(candidate, _availability,
                  thresholds={"renewable_pct": {"min": 50}, "latency_ms": {"max": max_latency}},
                  evidence_field="confirmed_renewable")


MANIFEST = {
    "name": "compute-power", "version": "1.0", "stages": ["route"],
    "candidate_schema": "schemas/candidate-compute.schema.json",
    "source_project": "github.com/sadpig70/SkyGrid",
}

SAMPLES = {
    "route": {
        "demand": {"workload_tflops": 10, "duration_hours": 2, "max_latency_ms": 150},
        "candidates": [
            {"name": "solar-farm-1", "grid_capacity_mw": 100, "renewable_pct": 80,
             "latency_ms": 100, "confirmed_renewable": True, "evidence_hash": "hA"},
            {"name": "wind-farm-2", "grid_capacity_mw": 200, "renewable_pct": 60,
             "latency_ms": 50, "confirmed_renewable": True, "evidence_hash": "hB"},
            {"name": "coal-3", "grid_capacity_mw": 300, "renewable_pct": 40,
             "latency_ms": 10, "confirmed_renewable": True, "evidence_hash": "hC"},
        ],
    },
}
