#!/usr/bin/env python3
"""InferenceGridPack — route AI inference demand as a grid-planning primitive.

source_project: github.com/sadpig70/InferMesh
stages: route
"""

from ._base import score as kscore


def _value(c):
    return c["available_tflops"] * (c["renewable_pct"] / 100) / max(c["marginal_grid_cost"], 1e-9)


def score(candidate, P=None):
    return kscore(candidate, _value, thresholds={"renewable_pct": {"min": 30}})


MANIFEST = {
    "name": "inference-grid", "version": "1.0", "stages": ["route"],
    "candidate_schema": "schemas/candidate-inference.schema.json",
    "source_project": "github.com/sadpig70/InferMesh",
}

SAMPLES = {
    "route": {
        "demand": {"tokens_per_s": 5000},
        "candidates": [
            {"name": "region-hydro", "available_tflops": 400, "renewable_pct": 90, "marginal_grid_cost": 2.0},
            {"name": "region-mixed", "available_tflops": 800, "renewable_pct": 50, "marginal_grid_cost": 5.0},
        ],
    },
}
