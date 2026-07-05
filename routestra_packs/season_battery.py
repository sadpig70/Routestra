#!/usr/bin/env python3
"""SeasonBatteryPack — bound a DAC-as-energy-source storage site.

source_project: github.com/sadpig70/SeasonBat
stages: bound
"""

from ._base import compliant, restricted, violation


def _dim(dimension, value, limit, near=0.9):
    if value > limit:
        return violation(dimension, f"{dimension} over limit")
    if value > limit * near:
        return restricted(dimension, f"{dimension} near limit")
    return compliant(dimension)


def bounds(telemetry, P=None):
    return [
        _dim("firm_power", telemetry["firm_draw_mw"], telemetry["supply_mw"]),
        _dim("storage_cycle", telemetry["cycle_depth"], telemetry["cycle_capacity"]),
    ]


MANIFEST = {
    "name": "season-battery", "version": "1.0", "stages": ["bound"],
    "candidate_schema": "schemas/candidate-season.schema.json",
    "source_project": "github.com/sadpig70/SeasonBat",
}

SAMPLES = {
    "bound": {"telemetry": {"firm_draw_mw": 30, "supply_mw": 50,
                            "cycle_depth": 0.7, "cycle_capacity": 1.0}},
}
