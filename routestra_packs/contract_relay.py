#!/usr/bin/env python3
"""ContractRelayPack — route only fail-open-safe federated contract handoffs.

source_project: github.com/sadpig70/ContractRelay
stages: route

ROUTING FINDING (HELIX machine-aware routing): ContractRelay's core machine emits a
deterministic receipt for a handoff case: RELAYED when contract, custody, baseline,
and normalized-error checks all pass; BLOCKED/INVALID otherwise. That is a routing
selection primitive: choose a relay path only when its receipt proves the handoff can
leave the local system without fail-closed defects. It is therefore a Routestra route
pack, not an Attestra policy pack.
"""

from ._base import eligible_score, ineligible


def _value(candidate):
    """Score valid relay candidates by explicit confidence and deterministic token proof."""
    confidence = float(candidate.get("confidence", 1.0))
    token_bonus = 1.0 if len(str(candidate.get("relay_token", ""))) == 64 else 0.0
    verified_bonus = 1.0 if candidate.get("verified", True) else 0.0
    return confidence + token_bonus + verified_bonus


def score(candidate, P=None):
    """route-stage function.

    A handoff route is eligible iff the ContractRelay receipt is RELAYED, fail_closed is
    false, has no normalized errors/reasons, carries a 64-char relay token, and matches
    any demanded contract/source/target constraints.
    """
    name = candidate.get("name", "")
    value = _value(candidate)
    verified = bool(candidate.get("verified", True))
    demand = (P or {}).get("demand", {})

    if candidate.get("decision") != "RELAYED":
        return ineligible(name, value, "decision_not_relayed", verified=verified)
    if candidate.get("fail_closed") is not False:
        return ineligible(name, value, "fail_closed", verified=verified)
    if candidate.get("errors") or candidate.get("reasons"):
        return ineligible(name, value, "receipt_has_defects", verified=verified)
    if len(str(candidate.get("relay_token", ""))) != 64:
        return ineligible(name, value, "relay_token_invalid", verified=False)
    for key in ("contract_id", "source", "target"):
        demand_key = f"required_{key}"
        if demand.get(demand_key) and candidate.get(key) != demand[demand_key]:
            return ineligible(name, value, f"{key}_mismatch", verified=verified)
    return eligible_score(name, value)


MANIFEST = {
    "name": "contract-relay", "version": "1.0", "stages": ["route"],
    "candidate_schema": "schemas/candidate-contractrelay.schema.json",
    "source_project": "github.com/sadpig70/ContractRelay",
}

SAMPLES = {
    "route": {
        "demand": {"required_contract_id": "contract-v1", "required_target": "system-b"},
        "candidates": [
            {
                "name": "relay-ok",
                "decision": "RELAYED",
                "fail_closed": False,
                "errors": [],
                "reasons": [],
                "relay_token": "a" * 64,
                "source": "system-a",
                "target": "system-b",
                "contract_id": "contract-v1",
                "route_id": "route-ab",
                "verified": True,
                "confidence": 1.0,
            },
            {
                "name": "relay-blocked",
                "decision": "BLOCKED",
                "fail_closed": True,
                "errors": [{"code": "HANDOFF_UNCONFIRMED"}],
                "reasons": [],
                "relay_token": "",
                "source": "system-a",
                "target": "system-c",
                "contract_id": "contract-v1",
                "route_id": "",
                "verified": True,
                "confidence": 0.9,
            },
        ],
    },
}
