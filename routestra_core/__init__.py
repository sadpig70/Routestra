"""Routestra kernel — single-source deterministic resource-routing substrate.

stdlib only. Time is injected (`now`); hashes exclude wall-time metadata. Domain
formulas (score/bounds) plug in via the pack contract. Third of the -stra family
(Attestra attests, Clearstra clears, Routestra routes) — shared severity algebra.
"""

from .candidate import validate_candidate, validate_pool
from .score import score, eligible_score, ineligible, check_thresholds
from .route import route
from .bound import bound, compliant, restricted, violation
from .verdict import SEVERITY, ATTESTRA_MAP, to_attestra_verdict, worst_of
from .provenance import verify_provenance
from .ledger import canonical_json, sha256, append_routing, build_record, verify_ledger
from .fingerprint import normalize, fingerprint, fingerprint_pack

__all__ = [
    "validate_candidate", "validate_pool",
    "score", "eligible_score", "ineligible", "check_thresholds",
    "route",
    "bound", "compliant", "restricted", "violation",
    "SEVERITY", "ATTESTRA_MAP", "to_attestra_verdict", "worst_of",
    "verify_provenance",
    "canonical_json", "sha256", "append_routing", "build_record", "verify_ledger",
    "normalize", "fingerprint", "fingerprint_pack",
]
