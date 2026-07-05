#!/usr/bin/env python3
"""Provenance — verify a routing plan against a confirmed evidence chain.

Generalizes SkyGrid.verify_provenance: the selected candidate's evidence must appear,
confirmed, in the chain. Pure stdlib.
"""


def verify_provenance(plan, chain):
    """Return {provenance_valid, chain_length, selected}."""
    selected = plan.get("selected")
    evidence = plan.get("selected_evidence")
    link = next((l for l in chain
                 if l.get("evidence_hash") == evidence and l.get("confirmed")), None)
    return {
        "provenance_valid": selected is not None and link is not None,
        "chain_length": len(chain),
        "selected": selected,
        "selected_evidence": evidence,
    }
