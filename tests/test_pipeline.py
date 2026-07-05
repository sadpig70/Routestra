#!/usr/bin/env python3
"""Phase 4 — RouteRun pipeline, candidate_schema enforcement, and docs consistency."""

import os
import tempfile
import unittest

from routestra_packs.loader import load_packs
from routestra_run import route_run, pack_inputs_from_samples

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")


class TestPipeline(unittest.TestCase):
    def setUp(self):
        self.reg = load_packs()

    def test_compute_power_route_with_provenance_and_ledger(self):
        pack = self.reg["packs"]["compute-power"]
        chain = [{"evidence_hash": "hB", "confirmed": True}]   # wind-farm-2's evidence
        with tempfile.TemporaryDirectory() as d:
            ledger = os.path.join(d, "r.jsonl")
            out = route_run(pack, pack_inputs_from_samples(pack), now="T",
                            ledger_path=ledger, subject="CP-1", chain=chain)
            self.assertEqual(out["stages"]["route"]["selected"], "wind-farm-2")
            self.assertTrue(out["provenance"]["provenance_valid"])
            self.assertEqual(len(out["ledger_records"]), 2)   # route + verify
            self.assertTrue(out["chain"]["valid"])

    def test_thermal_cascade_bound_with_ledger(self):
        pack = self.reg["packs"]["thermal-cascade"]
        with tempfile.TemporaryDirectory() as d:
            ledger = os.path.join(d, "r.jsonl")
            out = route_run(pack, pack_inputs_from_samples(pack), now="T", ledger_path=ledger)
            self.assertEqual(out["stages"]["bound"]["verdict"], "compliant")
            self.assertEqual(len(out["ledger_records"]), 1)
            self.assertTrue(out["chain"]["valid"])

    def test_idempotent_ledger(self):
        pack = self.reg["packs"]["compute-power"]
        with tempfile.TemporaryDirectory() as d:
            l1, l2 = os.path.join(d, "a.jsonl"), os.path.join(d, "b.jsonl")
            route_run(pack, pack_inputs_from_samples(pack), now="AAA", ledger_path=l1)
            route_run(pack, pack_inputs_from_samples(pack), now="ZZZ", ledger_path=l2)
            import json
            with open(l1, encoding="utf-8") as f:
                h1 = [json.loads(x)["record_hash"] for x in f]
            with open(l2, encoding="utf-8") as f:
                h2 = [json.loads(x)["record_hash"] for x in f]
            self.assertEqual(h1, h2)   # now excluded from record_hash


class TestCandidateSchemaEnforcement(unittest.TestCase):
    def test_all_packs_have_existing_schema(self):
        reg = load_packs()
        self.assertEqual(reg["errors"], [])
        for p in reg["packs"].values():
            self.assertTrue(os.path.exists(os.path.join(ROOT, p["candidate_schema"])))


class TestDocs(unittest.TestCase):
    def _read(self, name):
        with open(os.path.join(DOCS, name), "r", encoding="utf-8") as f:
            return f.read()

    def test_three_docs_substantial(self):
        for name in ("ARCHITECTURE.md", "PACK-CONTRACT.md", "DETERMINISM.md"):
            self.assertTrue(os.path.exists(os.path.join(DOCS, name)))
            self.assertGreater(len(self._read(name)), 800)

    def test_pack_contract_matches_code(self):
        txt = self._read("PACK-CONTRACT.md")
        for key in ("name", "version", "stages", "candidate_schema", "source_project"):
            self.assertIn(key, txt)
        for fn in ("score", "bounds", "compliant", "restricted", "violation"):
            self.assertIn(fn, txt)

    def test_determinism_doc_terms(self):
        txt = self._read("DETERMINISM.md")
        for term in ("random", "socket", "datetime.now", "record_hash", "math"):
            self.assertIn(term, txt)


if __name__ == "__main__":
    unittest.main()
