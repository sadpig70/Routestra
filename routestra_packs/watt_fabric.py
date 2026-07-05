#!/usr/bin/env python3
"""WattFabricPack — route AI workloads across DCs by cost/carbon/latency/sovereignty.

source_project: github.com/sadpig70/WattWeaveAI
stages: route
"""

from ._base import score as kscore


def _value(c):
    return (c["perf"] / max(c["cost"], 1e-9)) * (1 - c["carbon"]) * max(0, 1 - c["latency_ms"] / 500)


def score(candidate, P=None):
    return kscore(candidate, _value,
                  thresholds={"sovereignty_ok": {"eq": True}, "chip_available": {"eq": True}})


MANIFEST = {
    "name": "watt-fabric", "version": "1.0", "stages": ["route"],
    "candidate_schema": "schemas/candidate-fabric.schema.json",
    "source_project": "github.com/sadpig70/WattWeaveAI",
}

SAMPLES = {
    "route": {
        "demand": {"job": "train"},
        "candidates": [
            {"name": "eu-sovereign", "perf": 100, "cost": 10, "carbon": 0.2, "latency_ms": 100,
             "sovereignty_ok": True, "chip_available": True},
            {"name": "us-cheap", "perf": 120, "cost": 8, "carbon": 0.5, "latency_ms": 200,
             "sovereignty_ok": False, "chip_available": True},
        ],
    },
}
