#!/usr/bin/env python3
"""Verdict severity algebra + -stra family alignment.

Routestra bound verdicts (compliant < restricted < violation) share the same severity
shape as Attestra (valid < thin < breach). `to_attestra_verdict` maps them so a routing
decision can be attested by the -stra family. Pure stdlib.
"""

SEVERITY = {"compliant": 0, "restricted": 1, "violation": 2}

# alignment with Attestra's verdict scheme (the -stra platform family shares this algebra)
ATTESTRA_MAP = {"compliant": "valid", "restricted": "thin", "violation": "breach"}


def to_attestra_verdict(verdict):
    return ATTESTRA_MAP[verdict]


def worst_of(verdicts):
    """Highest-severity verdict among a list of verdict strings."""
    return max(verdicts, key=lambda v: SEVERITY[v]) if verdicts else "restricted"
