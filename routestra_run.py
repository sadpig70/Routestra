#!/usr/bin/env python3
"""RouteRun — run a pack's declared stages end-to-end.

route/bound -> (provenance verify for route) -> routing ledger. Meta/IO layer:
file I/O + injected `now`, clock-free.
"""

from routestra_core.ledger import append_routing, verify_ledger
from routestra_core.provenance import verify_provenance
from routestra_packs.loader import run_stage


def route_run(pack, inputs, now="", ledger_path=None, subject=None, chain=None):
    """Run every declared stage the caller supplied inputs for.

    inputs: {"route": {demand, candidates}, "bound": {telemetry}}  (any subset the pack declares)
    chain: optional evidence chain; when the pack routed, provenance is verified against it.
    Returns {pack, stages, ledger_records, provenance?, chain?}.
    """
    pid = subject or f"{pack['name']}-run"
    out = {"pack": pack["name"], "stages": {}, "ledger_records": []}
    for stage in ("route", "bound"):
        if stage not in pack["stages"] or stage not in inputs:
            continue
        result = run_stage(pack, stage, inputs[stage], now=now)
        out["stages"][stage] = result
        if ledger_path:
            rec = append_routing(ledger_path, result, pack["name"], stage, now=now, subject=pid)
            out["ledger_records"].append({"kind": stage, "index": rec["index"]})
    if "route" in out["stages"] and chain is not None:
        prov = verify_provenance(out["stages"]["route"], chain)
        out["provenance"] = prov
        if ledger_path:
            rec = append_routing(ledger_path, prov, pack["name"], "verify", now=now, subject=pid)
            out["ledger_records"].append({"kind": "verify", "index": rec["index"]})
    if ledger_path:
        out["chain"] = verify_ledger(ledger_path)
    return out


def pack_inputs_from_samples(pack):
    return {stage: pack["samples"][stage] for stage in pack["stages"]
            if stage in pack.get("samples", {})}
