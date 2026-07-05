#!/usr/bin/env python3
"""ClimateResiliencePack — score an asset's climate resilience like cyber-risk.

source_project: github.com/sadpig70/ClimateMesh
stages: bound
Threats, inherent risk, mitigating controls, residual risk, control gaps.
"""

from ._base import compliant, restricted, violation


def bounds(telemetry, P=None):
    inherent = telemetry["threat"] * telemetry["inherent_risk"]
    residual = inherent * (1 - telemetry["controls"])
    limit = telemetry.get("residual_limit", 0.3)
    if residual > limit:
        residual_dim = violation("residual_risk", f"residual {residual:.3f} over limit {limit}")
    elif residual > limit * 0.8:
        residual_dim = restricted("residual_risk", "residual near limit")
    else:
        residual_dim = compliant("residual_risk")
    gap = telemetry.get("control_gap", 0)
    gap_dim = (violation("control_gap", "control gap open") if gap > 0.5
               else compliant("control_gap"))
    return [residual_dim, gap_dim]


MANIFEST = {
    "name": "climate-resilience", "version": "1.0", "stages": ["bound"],
    "candidate_schema": "schemas/candidate-climate.schema.json",
    "source_project": "github.com/sadpig70/ClimateMesh",
}

SAMPLES = {
    "bound": {"telemetry": {"threat": 0.6, "inherent_risk": 0.5, "controls": 0.7,
                            "residual_limit": 0.3, "control_gap": 0.2}},
}
