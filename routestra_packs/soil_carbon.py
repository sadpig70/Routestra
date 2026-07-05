#!/usr/bin/env python3
"""SoilCarbonPack — route regeneration funding to the highest-impact parcels.

source_project: github.com/sadpig70/SoilBond
stages: route
"""

from ._base import score as kscore


def _value(c):
    return c["soil_carbon_reduction"] * c["resilience_score"]


def score(candidate, P=None):
    return kscore(candidate, _value, thresholds={"verifiable_reduction": {"eq": True}})


MANIFEST = {
    "name": "soil-carbon", "version": "1.0", "stages": ["route"],
    "candidate_schema": "schemas/candidate-soil.schema.json",
    "source_project": "github.com/sadpig70/SoilBond",
}

SAMPLES = {
    "route": {
        "demand": {"fund_pool": 100000},
        "candidates": [
            {"name": "parcel-north", "soil_carbon_reduction": 120, "resilience_score": 0.8,
             "verifiable_reduction": True},
            {"name": "parcel-south", "soil_carbon_reduction": 200, "resilience_score": 0.3,
             "verifiable_reduction": True},
            {"name": "parcel-unverified", "soil_carbon_reduction": 300, "resilience_score": 0.9,
             "verifiable_reduction": False},
        ],
    },
}
