#!/usr/bin/env python3
"""WasteStackPack — bound the two stacked cashflows on a stranded datacenter site.

source_project: github.com/sadpig70/WasteStack
stages: bound
"""

from ._base import compliant, restricted, violation


def _dim(dimension, value, limit, near=0.9):
    if value > limit:
        return violation(dimension, f"{dimension} over capacity")
    if value > limit * near:
        return restricted(dimension, f"{dimension} near capacity")
    return compliant(dimension)


def bounds(telemetry, P=None):
    return [
        _dim("grid_interconnect", telemetry["tenant_draw_mw"], telemetry["interconnect_mw"]),
        _dim("heat_offtake", telemetry["heat_output_mw"], telemetry["offtake_capacity_mw"]),
    ]


MANIFEST = {
    "name": "waste-stack", "version": "1.0", "stages": ["bound"],
    "candidate_schema": "schemas/candidate-waste.schema.json",
    "source_project": "github.com/sadpig70/WasteStack",
}

SAMPLES = {
    "bound": {"telemetry": {"tenant_draw_mw": 95, "interconnect_mw": 100,
                            "heat_output_mw": 40, "offtake_capacity_mw": 60}},
}
