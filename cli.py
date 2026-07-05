#!/usr/bin/env python3
"""Routestra CLI — pack / run / stage / verify / determinism.

stdlib only. `now` is injected via --now (default ""), never read from the clock.
"""

import argparse
import json
import os
import sys

from routestra_core.ledger import verify_ledger
from routestra_core.determinism import check_tree
from routestra_packs.loader import load_packs, get_pack, run_stage
from routestra_run import route_run, pack_inputs_from_samples

ROOT = os.path.dirname(os.path.abspath(__file__))


def _default(o):
    if o == float("inf"):
        return "inf"
    raise TypeError


def _dump(obj):
    print(json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True, default=_default))


def _load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def cmd_pack(args, reg):
    _dump({
        "packs": [
            {"name": p["name"], "version": p["version"], "stages": p["stages"],
             "source_project": p["source_project"], "fingerprint": p["fingerprint"][:16]}
            for p in reg["packs"].values()
        ],
        "dropped": reg["dropped"], "errors": reg["errors"],
    })
    return 0


def cmd_run(args, reg):
    pack = get_pack(reg, args.pack)
    inputs = _load_json(args.input) if args.input else pack_inputs_from_samples(pack)
    chain = _load_json(args.chain) if args.chain else None
    result = route_run(pack, inputs, now=args.now, ledger_path=args.ledger,
                       subject=args.subject, chain=chain)
    _dump(result)
    if args.ledger and not result.get("chain", {}).get("valid", True):
        return 2
    return 0


def cmd_stage(args, reg):
    pack = get_pack(reg, args.pack)
    inputs = _load_json(args.input) if args.input else pack["samples"].get(args.stage, {})
    _dump(run_stage(pack, args.stage, inputs, now=args.now))
    return 0


def cmd_verify(args, _reg):
    report = verify_ledger(args.ledger)
    _dump(report)
    return 0 if report["valid"] else 1


def cmd_determinism(_args, _reg):
    report = check_tree(ROOT)
    _dump(report)
    return 0 if report["clean"] else 1


def build_parser():
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--now", default="", help="injected timestamp metadata (default empty)")

    p = argparse.ArgumentParser(prog="routestra", parents=[common],
                                description="Deterministic resource-routing platform")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("pack", parents=[common], help="list loaded packs").add_argument("list", nargs="?")

    s = sub.add_parser("run", parents=[common], help="run a pack's pipeline (route/bound + verify)")
    s.add_argument("--pack", required=True)
    s.add_argument("--input", help="JSON inputs {stage: {...}} (default: pack samples)")
    s.add_argument("--chain", help="JSON evidence chain for provenance verify")
    s.add_argument("--ledger", help="routing ledger path")
    s.add_argument("--subject")

    s = sub.add_parser("stage", parents=[common], help="run one stage of a pack")
    s.add_argument("--pack", required=True)
    s.add_argument("--stage", required=True, choices=["route", "bound"])
    s.add_argument("--input")

    s = sub.add_parser("verify", parents=[common], help="verify a routing ledger's hash chain")
    s.add_argument("--ledger", required=True)

    sub.add_parser("determinism", parents=[common], help="scan kernel+packs for boundary violations")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    reg = load_packs()
    dispatch = {"pack": cmd_pack, "run": cmd_run, "stage": cmd_stage,
                "verify": cmd_verify, "determinism": cmd_determinism}
    return dispatch[args.cmd](args, reg)


if __name__ == "__main__":
    raise SystemExit(main())
