#!/usr/bin/env python3
"""PackContract — manifest/stage validation, dedup, and stage dispatch through the kernel.

Phase 2 verifies the contract with an in-memory synthetic pack (no Phase-3 packs pulled
forward). It exercises both stages: route and bound.
"""

import types
import unittest

from routestra_packs.loader import validate_module, load_packs, run_stage, get_pack, STAGE_FN
from routestra_packs import _base


def _fake_pack():
    """A synthetic two-stage routing pack (SimpleNamespace stands in for a module)."""
    def _availability(c):
        return c["grid_capacity_mw"] * (c["renewable_pct"] / 100) * max(0, 1 - c["latency_ms"] / 200)

    def score(candidate, P=None):
        max_latency = (P or {}).get("demand", {}).get("max_latency_ms", 200)
        return _base.score(candidate, _availability,
                           thresholds={"renewable_pct": {"min": 50}, "latency_ms": {"max": max_latency}},
                           evidence_field="confirmed_renewable")

    def bounds(telemetry, P=None):
        dims = []
        if telemetry["power_mw"] <= telemetry["grid_limit_mw"]:
            dims.append(_base.compliant("power"))
        else:
            dims.append(_base.violation("power", "over grid limit"))
        if telemetry["thermal_c"] <= telemetry["thermal_limit_c"]:
            dims.append(_base.compliant("thermal"))
        elif telemetry["thermal_c"] <= telemetry["thermal_limit_c"] * 1.1:
            dims.append(_base.restricted("thermal", "near limit"))
        else:
            dims.append(_base.violation("thermal", "over dispersion threshold"))
        return dims

    return types.SimpleNamespace(
        MANIFEST={"name": "fake", "version": "1.0", "stages": ["route", "bound"],
                  "candidate_schema": "schemas/candidate-fake.schema.json",
                  "source_project": "github.com/sadpig70/Fake"},
        score=score, bounds=bounds, SAMPLES={},
    )


class TestValidation(unittest.TestCase):
    def test_valid_module(self):
        manifest, fns, err = validate_module(_fake_pack(), "fake")
        self.assertEqual(err, "")
        self.assertEqual(set(fns), {"route", "bound"})

    def test_missing_stage_function(self):
        mod = _fake_pack()
        del mod.bounds
        _, _, err = validate_module(mod, "fake")
        self.assertIn("bound", err)

    def test_bad_stages(self):
        mod = _fake_pack()
        mod.MANIFEST = {**mod.MANIFEST, "stages": ["route", "teleport"]}
        _, _, err = validate_module(mod, "fake")
        self.assertIn("stages", err)

    def test_stage_fn_map(self):
        self.assertEqual(STAGE_FN, {"route": "score", "bound": "bounds"})


class TestRunStage(unittest.TestCase):
    def setUp(self):
        manifest, fns, _ = validate_module(_fake_pack(), "fake")
        self.pack = {**manifest, "fns": fns}

    def test_route(self):
        candidates = [
            {"name": "locA", "grid_capacity_mw": 100, "renewable_pct": 80, "latency_ms": 100,
             "confirmed_renewable": True, "evidence_hash": "hA"},
            {"name": "locB", "grid_capacity_mw": 200, "renewable_pct": 60, "latency_ms": 50,
             "confirmed_renewable": True, "evidence_hash": "hB"},
        ]
        r = run_stage(self.pack, "route",
                      {"demand": {"max_latency_ms": 150}, "candidates": candidates}, now="T")
        self.assertEqual(r["selected"], "locB")   # 90 > 40

    def test_bound(self):
        r = run_stage(self.pack, "bound", {"telemetry": {
            "power_mw": 120, "grid_limit_mw": 100,      # over -> violation
            "thermal_c": 30, "thermal_limit_c": 40}}, now="T")
        self.assertEqual(r["verdict"], "violation")
        self.assertEqual(r["worst"], "power")

    def test_unimplemented_stage_raises(self):
        pack = {"name": "x", "fns": {"route": lambda c, P: {}}}
        with self.assertRaises(ValueError):
            run_stage(pack, "bound", {})


class TestRegistry(unittest.TestCase):
    def test_package_loads_cleanly(self):
        reg = load_packs()  # real packs exist from Phase 3; contract must load them cleanly
        self.assertEqual(reg["errors"], [])
        self.assertEqual(reg["dropped"], [])
        for p in reg["packs"].values():
            self.assertTrue(p["stages"] and "fns" in p)

    def test_get_pack_unknown_raises(self):
        with self.assertRaises(KeyError):
            get_pack({"packs": {}}, "nope")


if __name__ == "__main__":
    unittest.main()
