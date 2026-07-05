#!/usr/bin/env python3
"""RoutestraCore kernel tests — score, route, bound, verdict, provenance, ledger,
fingerprint, determinism. Route scoring mirrors SkyGrid; bound mirrors ThermalCascadeBound."""

import os
import tempfile
import unittest

from routestra_core import (
    score, check_thresholds, route, bound, compliant, restricted, violation,
    SEVERITY, to_attestra_verdict, verify_provenance,
    append_routing, verify_ledger, build_record, fingerprint_pack, validate_pool,
)
from routestra_core.determinism import check_tree

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _availability(c):
    # SkyGrid: grid_capacity_mw * (renewable_pct/100) * max(0, 1 - latency_ms/200)
    return c["grid_capacity_mw"] * (c["renewable_pct"] / 100) * max(0, 1 - c["latency_ms"] / 200)


def _skygrid_score_fn(max_latency):
    def fn(c):
        return score(c, _availability,
                     thresholds={"renewable_pct": {"min": 50}, "latency_ms": {"max": max_latency}},
                     evidence_field="confirmed_renewable")
    return fn


CANDIDATES = [
    {"name": "locA", "grid_capacity_mw": 100, "renewable_pct": 80, "latency_ms": 100,
     "confirmed_renewable": True, "evidence_hash": "hA"},
    {"name": "locB", "grid_capacity_mw": 200, "renewable_pct": 60, "latency_ms": 50,
     "confirmed_renewable": True, "evidence_hash": "hB"},
    {"name": "locC", "grid_capacity_mw": 300, "renewable_pct": 40, "latency_ms": 10,
     "confirmed_renewable": True, "evidence_hash": "hC"},   # renewable < 50 -> ineligible
    {"name": "locD", "grid_capacity_mw": 150, "renewable_pct": 90, "latency_ms": 100,
     "confirmed_renewable": False, "evidence_hash": "hD"},  # not verified -> ineligible
]


class TestScore(unittest.TestCase):
    def test_eligible(self):
        r = score(CANDIDATES[0], _availability,
                  thresholds={"renewable_pct": {"min": 50}}, evidence_field="confirmed_renewable")
        self.assertTrue(r["eligible"])
        self.assertEqual(r["score"], 40.0)   # 100*0.8*0.5

    def test_threshold_fail(self):
        r = score(CANDIDATES[2], _availability,
                  thresholds={"renewable_pct": {"min": 50}}, evidence_field="confirmed_renewable")
        self.assertFalse(r["eligible"])
        self.assertEqual(r["reason"], "renewable_pct_below_min")

    def test_evidence_fail(self):
        r = score(CANDIDATES[3], _availability, evidence_field="confirmed_renewable")
        self.assertFalse(r["eligible"])
        self.assertEqual(r["reason"], "evidence_not_verified")

    def test_check_thresholds_deterministic(self):
        self.assertEqual(check_thresholds({"a": 5}, {"a": {"max": 3}}), (False, "a_above_max"))


class TestRoute(unittest.TestCase):
    def test_selects_best_eligible(self):
        r = route({"max_latency_ms": 150}, CANDIDATES, _skygrid_score_fn(150), now="T")
        self.assertEqual(r["selected"], "locB")     # 90 > locA 40; locC/locD ineligible
        self.assertEqual(r["selected_score"], 90.0)  # 200*0.6*0.75
        self.assertEqual(r["selected_evidence"], "hB")

    def test_no_eligible(self):
        r = route({"max_latency_ms": 5}, CANDIDATES, _skygrid_score_fn(5), now="T")
        self.assertIsNone(r["selected"])            # every latency > 5

    def test_deterministic_tiebreak(self):
        tie = [{"name": "Zeta", "v": 1, "evidence_hash": "z"},
               {"name": "Alpha", "v": 1, "evidence_hash": "a"}]
        r = route({}, tie, lambda c: {"name": c["name"], "score": 5, "eligible": True,
                                      "verified": True, "reason": ""}, now="T")
        self.assertEqual(r["selected"], "Alpha")    # equal score -> name ascending

    def test_invalid_pool_raises(self):
        with self.assertRaises(ValueError):
            route({}, [{"name": "X"}, {"name": "X"}],
                  lambda c: {"name": c["name"], "score": 1, "eligible": True, "verified": True, "reason": ""})
        self.assertFalse(validate_pool("nope")["ok"])


class TestBound(unittest.TestCase):
    def test_severity_merge(self):
        self.assertEqual(bound([compliant("power"), violation("thermal", "over")])["verdict"], "violation")
        self.assertEqual(bound([compliant("power"), restricted("thermal", "near")])["verdict"], "restricted")
        self.assertEqual(bound([compliant("a"), compliant("b")])["verdict"], "compliant")

    def test_worst_dimension_surfaced(self):
        self.assertEqual(bound([compliant("power"), violation("thermal", "x")])["worst"], "thermal")

    def test_severity_map_matches_thermalcascadebound(self):
        self.assertEqual(SEVERITY, {"compliant": 0, "restricted": 1, "violation": 2})


class TestVerdictAlignment(unittest.TestCase):
    def test_attestra_map(self):
        self.assertEqual(to_attestra_verdict("compliant"), "valid")
        self.assertEqual(to_attestra_verdict("restricted"), "thin")
        self.assertEqual(to_attestra_verdict("violation"), "breach")


class TestProvenance(unittest.TestCase):
    def test_valid(self):
        plan = {"selected": "locB", "selected_evidence": "hB"}
        chain = [{"evidence_hash": "hB", "confirmed": True}]
        self.assertTrue(verify_provenance(plan, chain)["provenance_valid"])

    def test_unconfirmed(self):
        plan = {"selected": "locB", "selected_evidence": "hB"}
        chain = [{"evidence_hash": "hB", "confirmed": False}]
        self.assertFalse(verify_provenance(plan, chain)["provenance_valid"])


class TestLedger(unittest.TestCase):
    def _res(self, s):
        return {"selected": s, "routed_at": "X"}

    def test_chain_and_time_independent(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "r.jsonl")
            append_routing(p, self._res("locB"), "compute-power", "route", now="T1")
            append_routing(p, self._res("locA"), "compute-power", "route", now="T2")
            self.assertTrue(verify_ledger(p)["valid"])
        a = build_record("", self._res("x"), "m", "route", now="AAA")
        b = build_record("", self._res("x"), "m", "route", now="ZZZ")
        self.assertEqual(a["record_hash"], b["record_hash"])

    def test_tamper(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "r.jsonl")
            append_routing(p, self._res("locB"), "m", "route", now="T1")
            append_routing(p, self._res("locA"), "m", "route", now="T2")
            with open(p, "r", encoding="utf-8") as f:
                lines = f.readlines()
            lines[0] = lines[0].replace('"route"', '"bound"')
            with open(p, "w", encoding="utf-8") as f:
                f.writelines(lines)
            self.assertFalse(verify_ledger(p)["valid"])


class TestFingerprint(unittest.TestCase):
    def test_same_source_collides(self):
        a = {"source_project": "github.com/sadpig70/SkyGrid", "stages": ["route"], "candidate_schema": "s"}
        b = {"source_project": "github.com/sadpig70/SkyGrid", "stages": ["route"], "candidate_schema": "s"}
        self.assertEqual(fingerprint_pack(a), fingerprint_pack(b))

    def test_distinct_sources_differ(self):
        a = {"source_project": "github.com/sadpig70/SkyGrid", "stages": ["route"], "candidate_schema": "s"}
        b = {"source_project": "github.com/sadpig70/InferMesh", "stages": ["route"], "candidate_schema": "s"}
        self.assertNotEqual(fingerprint_pack(a), fingerprint_pack(b))


class TestDeterminism(unittest.TestCase):
    def test_kernel_deterministic(self):
        rep = check_tree(ROOT)
        self.assertTrue(rep["clean"], f"violations: {rep['violations']}")
        self.assertGreater(rep["files_scanned"], 6)


if __name__ == "__main__":
    unittest.main()
