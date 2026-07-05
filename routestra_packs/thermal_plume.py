#!/usr/bin/env python3
"""ThermalPlumePack — plan marine thermal-discharge dispersion siting.

source_project: github.com/sadpig70/ThermalPlumeStage
stages: bound
"""

from ._base import compliant, restricted, violation


def _dim(dimension, value, limit, near=0.9):
    if value > limit:
        return violation(dimension, f"{dimension} over threshold")
    if value > limit * near:
        return restricted(dimension, f"{dimension} near threshold")
    return compliant(dimension)


def bounds(telemetry, P=None):
    return [
        _dim("discharge_temp", telemetry["discharge_temp_c"], telemetry["temp_limit_c"]),
        _dim("dilution", telemetry["plume_radius_m"], telemetry["dilution_window_m"]),
    ]


MANIFEST = {
    "name": "thermal-plume", "version": "1.0", "stages": ["bound"],
    "candidate_schema": "schemas/candidate-plume.schema.json",
    "source_project": "github.com/sadpig70/ThermalPlumeStage",
}

SAMPLES = {
    "bound": {"telemetry": {"discharge_temp_c": 28, "temp_limit_c": 32,
                            "plume_radius_m": 400, "dilution_window_m": 500}},
}
