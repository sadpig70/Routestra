#!/usr/bin/env python3
"""Parity anchor: routestra_packs.flow_mesh vs the real FlowMesh reference.

FlowMesh is an independent repo (github.com/sadpig70/FlowMesh); it is not vendored in
Routestra. When its source is importable in a dev checkout, this test asserts the pack's
bound verdict reproduces FlowMesh's flow posture exactly across pipelines spanning every
branch (balanced / constrained / critical). In CI (source absent) it skips.

Point FLOWMESH_SRC at the project's ``src`` dir to run it, e.g.
    FLOWMESH_SRC=D:/IdeaFirst/flowmesh/src python -m unittest tests.test_flow_mesh_parity
"""

import os
import sys
import unittest

from routestra_packs.loader import load_packs, run_stage


def _load_flowmesh():
    candidates = [os.environ.get("FLOWMESH_SRC")]
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    candidates += [
        os.path.join(here, "..", "flowmesh", "src"),
        os.path.join(here, "..", "FlowMesh", "src"),
        "D:/IdeaFirst/flowmesh/src",
    ]
    for cand in candidates:
        if cand and os.path.isdir(cand) and cand not in sys.path:
            sys.path.insert(0, cand)
    try:
        from flowmesh import analyze as analyze_mod  # noqa: WPS433
        from flowmesh import models as models_mod  # noqa: WPS433
        return analyze_mod, models_mod
    except Exception:  # noqa: BLE001 — source simply not present here
        return None, None


_ANALYZE, _MODELS = _load_flowmesh()

# FlowMesh flow posture -> Routestra bound verdict.
_POSTURE_TO_VERDICT = {"balanced": "compliant", "constrained": "restricted",
                       "critical_bottleneck": "violation"}

# Pipelines exercising each branch: 0.8 balanced, 0.9 constrained, 1.25 critical.
_CASES = [
    {"input_rate": 80, "stages": [
        {"stage_id": "ingest", "constraint_type": "io", "capacity": 200},
        {"stage_id": "compute", "constraint_type": "compute", "capacity": 100}]},   # 0.8 -> balanced
    {"input_rate": 90, "stages": [
        {"stage_id": "compute", "constraint_type": "compute", "capacity": 100},
        {"stage_id": "net", "constraint_type": "network", "capacity": 150}]},       # 0.9 -> constrained
    {"input_rate": 125, "stages": [
        {"stage_id": "review", "constraint_type": "human_review", "capacity": 100},
        {"stage_id": "io", "constraint_type": "io", "capacity": 300}]},             # 1.25 -> critical
]


def _pipeline(spec, idx):
    return {"pipeline_id": f"P{idx}", "name": "t", "input_rate": spec["input_rate"],
            "unit_value": 1.0, "stages": spec["stages"]}


@unittest.skipUnless(_ANALYZE is not None, "FlowMesh source not importable (independent repo)")
class TestFlowMeshParity(unittest.TestCase):
    def setUp(self):
        self.pack = load_packs()["packs"]["flow-mesh"]

    def test_posture_matches_source(self):
        for idx, spec in enumerate(_CASES):
            with self.subTest(case=idx):
                pipeline = _MODELS.Pipeline.from_dict(_pipeline(spec, idx))
                posture = _ANALYZE.analyze(pipeline).posture.verdict
                expected = _POSTURE_TO_VERDICT[posture]

                result = run_stage(self.pack, "bound", {"telemetry": spec}, now="T")
                self.assertEqual(
                    result["verdict"], expected,
                    f"posture={posture} -> expected {expected}, got {result['verdict']} "
                    f"(worst={result.get('worst')})")


if __name__ == "__main__":
    unittest.main()
