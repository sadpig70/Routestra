#!/usr/bin/env python3
"""Parity anchor: routestra_packs.contract_relay vs real ContractRelay receipts."""

import os
import sys
import unittest

from routestra_packs.loader import load_packs, run_stage


def _load_contractrelay():
    candidates = [os.environ.get("CONTRACTRELAY_SRC")]
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    candidates += [
        os.path.join(here, "..", "ContractRelay", "src"),
        "D:/HELIX/ContractRelay/src",
    ]
    for cand in candidates:
        if cand and os.path.isdir(cand) and cand not in sys.path:
            sys.path.insert(0, cand)
    try:
        from contractrelay import relay  # noqa: WPS433
        from contractrelay.samples import sample_case  # noqa: WPS433
        return relay, sample_case
    except Exception:  # noqa: BLE001 — source simply not present here
        return None, None


_RELAY, _SAMPLE_CASE = _load_contractrelay()


def _candidate_from_receipt(receipt):
    contract_id = "contract-v1" if receipt["case_id"] else ""
    return {
        "name": receipt["case_id"] or receipt["decision"].lower(),
        "decision": receipt["decision"],
        "fail_closed": receipt["fail_closed"],
        "errors": receipt["errors"],
        "reasons": receipt["reasons"],
        "relay_token": receipt["relay_token"],
        "source": receipt["source"],
        "target": receipt["target"],
        "contract_id": contract_id,
        "route_id": "route-ab" if receipt["decision"] == "RELAYED" else "",
        "verified": True,
        "confidence": 1.0,
        "evidence_hash": receipt["receipt_sha256"],
    }


@unittest.skipUnless(_RELAY is not None, "ContractRelay source not importable")
class TestContractRelayParity(unittest.TestCase):
    def setUp(self):
        self.pack = load_packs()["packs"]["contract-relay"]

    def test_receipt_decisions_match_route_eligibility(self):
        expected = {"relayed": True, "blocked": False, "invalid-baseline": False}
        for kind, eligible in expected.items():
            with self.subTest(kind=kind):
                receipt = _RELAY(_SAMPLE_CASE(kind))
                result = run_stage(
                    self.pack,
                    "route",
                    {
                        "demand": {"required_contract_id": "contract-v1"},
                        "candidates": [_candidate_from_receipt(receipt)],
                    },
                    now="T",
                )
                self.assertEqual(result["selected"] is not None, eligible)

    def test_route_prefers_relayed_receipt_over_blocked_receipt(self):
        relayed = _candidate_from_receipt(_RELAY(_SAMPLE_CASE("relayed")))
        blocked = _candidate_from_receipt(_RELAY(_SAMPLE_CASE("blocked")))
        result = run_stage(
            self.pack,
            "route",
            {
                "demand": {"required_contract_id": "contract-v1", "required_target": "system-b"},
                "candidates": [blocked, relayed],
            },
            now="T",
        )
        self.assertEqual(result["selected"], "sample-relayed")
        self.assertEqual(result["selected_evidence"], relayed["evidence_hash"])


if __name__ == "__main__":
    unittest.main()
