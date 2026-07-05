#!/usr/bin/env python3
"""Shared helpers for routing packs. A pack module exposes MANIFEST + its stage
functions + SAMPLES.

Stage → function it must provide:
  route -> score(candidate, P) -> ScoreResult   (kernel route() ranks by this)
  bound -> bounds(telemetry, P) -> list[dim]    (kernel bound() merges by severity)

Packs compose scoring from the kernel primitives below; they never redefine
route/bound/ledger (that lives once in routestra_core).
"""

from routestra_core.score import score, eligible_score, ineligible, check_thresholds
from routestra_core.bound import compliant, restricted, violation

__all__ = [
    "score", "eligible_score", "ineligible", "check_thresholds",
    "compliant", "restricted", "violation",
]
