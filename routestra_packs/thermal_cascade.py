#!/usr/bin/env python3
"""ThermalCascadePack — reference bound pack. Parity with ThermalCascadeBound.

source_project: github.com/sadpig70/ThermalCascadeBound
stages: bound
Judges a co-located AI-datacenter + DAC site: power allocation vs grid limit and
low-grade thermal discharge vs ecological dispersion threshold, merged by severity.
"""

from ._base import compliant, restricted, violation


def _dim(dimension, value, limit, near=0.9):
    if value > limit:
        return violation(dimension, f"{dimension} over threshold")
    if value > limit * near:
        return restricted(dimension, f"{dimension} near threshold")
    return compliant(dimension)


def bounds(telemetry, P=None):
    """bound-stage function (kernel STAGE_FN: bound -> bounds)."""
    return [
        _dim("power", telemetry["power_alloc_mw"], telemetry["grid_limit_mw"]),
        _dim("thermal", telemetry["thermal_discharge_c"], telemetry["dispersion_limit_c"]),
    ]


MANIFEST = {
    "name": "thermal-cascade", "version": "1.0", "stages": ["bound"],
    "candidate_schema": "schemas/candidate-thermal.schema.json",
    "source_project": "github.com/sadpig70/ThermalCascadeBound",
}

SAMPLES = {
    "bound": {"telemetry": {"power_alloc_mw": 80, "grid_limit_mw": 100,
                            "thermal_discharge_c": 25, "dispersion_limit_c": 30}},
}
