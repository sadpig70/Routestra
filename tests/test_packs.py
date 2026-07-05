#!/usr/bin/env python3
"""Phase 3 packs — registry load, per-stage execution, reference parity."""

import os
import unittest

from routestra_core.determinism import check_tree
from routestra_packs.loader import load_packs, run_stage

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPECTED = {
    "compute-power", "power-roam", "inference-grid", "watt-fabric", "soil-carbon",
    "thermal-cascade", "thermal-plume", "waste-stack", "season-battery", "climate-resilience",
}


class TestRegistry(unittest.TestCase):
    def setUp(self):
        self.reg = load_packs()

    def test_all_packs_loaded(self):
        self.assertEqual(set(self.reg["packs"]), EXPECTED)

    def test_no_errors_or_drops(self):
        self.assertEqual(self.reg["errors"], [])
        self.assertEqual(self.reg["dropped"], [])

    def test_source_projects_tagged(self):
        for p in self.reg["packs"].values():
            self.assertTrue(p["source_project"].startswith("github.com/sadpig70/"))


class TestEveryStageRuns(unittest.TestCase):
    def test_declared_stages_execute(self):
        reg = load_packs()
        for name, pack in reg["packs"].items():
            for stage in pack["stages"]:
                self.assertIn(stage, pack["samples"], f"{name} missing sample for {stage}")
                result = run_stage(pack, stage, pack["samples"][stage], now="T")
                self.assertIsInstance(result, dict)
                if stage == "route":
                    self.assertIsNotNone(result["selected"], f"{name} route selected nothing")
                if stage == "bound":
                    self.assertIn(result["verdict"], ("compliant", "restricted", "violation"))


class TestComputePowerParity(unittest.TestCase):
    def test_skygrid_selection(self):
        m = load_packs()["packs"]["compute-power"]
        r = run_stage(m, "route", m["samples"]["route"], now="T")
        self.assertEqual(r["selected"], "wind-farm-2")   # availability 90 > solar 40; coal ineligible
        self.assertEqual(r["selected_score"], 90.0)
        self.assertEqual(r["selected_evidence"], "hB")


class TestThermalCascadeParity(unittest.TestCase):
    def setUp(self):
        self.m = load_packs()["packs"]["thermal-cascade"]

    def test_compliant_sample(self):
        r = run_stage(self.m, "bound", self.m["samples"]["bound"], now="T")
        self.assertEqual(r["verdict"], "compliant")

    def test_violation_merge(self):
        r = run_stage(self.m, "bound", {"telemetry": {
            "power_alloc_mw": 120, "grid_limit_mw": 100,          # over -> violation
            "thermal_discharge_c": 25, "dispersion_limit_c": 30}}, now="T")
        self.assertEqual(r["verdict"], "violation")
        self.assertEqual(r["worst"], "power")


class TestRouteSemantics(unittest.TestCase):
    def setUp(self):
        self.reg = load_packs()

    def test_watt_fabric_sovereignty_gate(self):
        m = self.reg["packs"]["watt-fabric"]
        r = run_stage(m, "route", m["samples"]["route"], now="T")
        self.assertEqual(r["selected"], "eu-sovereign")   # us-cheap fails sovereignty threshold

    def test_soil_carbon_verifiable_gate(self):
        m = self.reg["packs"]["soil-carbon"]
        r = run_stage(m, "route", m["samples"]["route"], now="T")
        self.assertEqual(r["selected"], "parcel-north")   # unverified parcel excluded despite higher raw


class TestDeterminism(unittest.TestCase):
    def test_packs_deterministic(self):
        rep = check_tree(ROOT)
        self.assertTrue(rep["clean"], f"violations: {rep['violations']}")


if __name__ == "__main__":
    unittest.main()
