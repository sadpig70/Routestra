#!/usr/bin/env python3
"""FlowMeshPack — pipeline bottleneck utilization as a Routestra bound pack.

source_project: github.com/sadpig70/FlowMesh
stages: bound

ROUTING FINDING (HELIX machine-aware routing): the "Compatibility Mesh" cluster shares
a name but not one machine. FlowMesh's core gate `_decide(utilization)` classifies a
computed physical metric (input_rate / bottleneck_capacity) against thresholds into
balanced / constrained / critical_bottleneck — a threshold-bound on a resource metric.
That is Routestra's `bound` machine (compliant/restricted/violation), NOT Attestra's
policy predicate gate. So FlowMesh routes to Routestra as a bound pack — cf. the rest of
the cluster: SovMesh/PqcMesh/SignalMesh -> Attestra gates; AgentMesh -> Clearstra pricing.
The routing thus spans three platforms, decided per-machine from real code.

Emitting one utilization dimension per stage and merging by Routestra bound()'s
max-severity reproduces FlowMesh's posture exactly: the binding constraint is the
min-capacity stage = the max-utilization stage = the highest-severity dimension.
balanced -> compliant, constrained -> restricted, critical_bottleneck -> violation.
See tests/test_flow_mesh_parity.py, which checks the pack against the real FlowMesh.
"""

from ._base import compliant, restricted, violation

# Bottleneck utilization thresholds (mirror FlowMesh.models).
CRITICAL_UTILIZATION = 1.0
CONSTRAINED_UTILIZATION = 0.85


def _util_dim(name, utilization):
    """FlowMesh._decide applied to one stage's utilization -> a bound dimension."""
    if utilization > CRITICAL_UTILIZATION:
        return violation(name, f"utilization {utilization:.2f} exceeds capacity (critical bottleneck)")
    if utilization >= CONSTRAINED_UTILIZATION:
        return restricted(name, f"utilization {utilization:.2f} near capacity (constrained)")
    return compliant(name, f"utilization {utilization:.2f} within capacity")


def bounds(telemetry, P=None):
    """bound-stage function (kernel STAGE_FN: bound -> bounds).

    One dimension per stage; the kernel's bound() merges them to the binding
    constraint's severity, which equals FlowMesh's bottleneck posture.
    """
    input_rate = float(telemetry["input_rate"])
    dims = []
    for s in telemetry.get("stages", []):
        cap = float(s["capacity"])
        name = s.get("stage_id") or s.get("constraint_type") or "stage"
        u = input_rate / cap if cap > 0 else float("inf")
        dims.append(_util_dim(name, u))
    return dims


MANIFEST = {
    "name": "flow-mesh", "version": "1.0", "stages": ["bound"],
    "candidate_schema": "schemas/candidate-flow.schema.json",
    "source_project": "github.com/sadpig70/FlowMesh",
}

SAMPLES = {
    # input_rate 80 vs binding capacity 100 -> utilization 0.8 -> balanced -> compliant
    "bound": {"telemetry": {"input_rate": 80, "stages": [
        {"stage_id": "ingest", "constraint_type": "io", "capacity": 200},
        {"stage_id": "compute", "constraint_type": "compute", "capacity": 100},
    ]}},
}
