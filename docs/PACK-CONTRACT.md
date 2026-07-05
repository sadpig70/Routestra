# Routestra Pack Contract

> How to author a routing pack. A pack projects one routing/siting domain onto the kernel.
> **Adding a pack requires no kernel change** — one module + one candidate schema.

## What a pack is

A module under `routestra_packs/` exposing:

| Name | Type | Meaning |
|---|---|---|
| `MANIFEST` | `dict` | pack metadata (below) |
| stage functions | callables | one per declared stage |
| `SAMPLES` | `dict[stage, dict]` | example inputs per stage, for `run_stage` |

The loader (`routestra_packs/loader.py`) auto-discovers modules, validates the contract,
checks the declared `candidate_schema` file exists, and dedups by fingerprint.

## MANIFEST

```python
MANIFEST = {
    "name": "my-domain",                       # unique (kebab-case)
    "version": "1.0",
    "stages": ["route"],                       # subset of route / bound
    "candidate_schema": "schemas/candidate-my.schema.json",  # must exist (loader errors otherwise)
    "source_project": "github.com/sadpig70/MyDomain",
}
```

## Stages → the function each requires

| Stage | Function you provide | Signature | Kernel uses it via |
|---|---|---|---|
| `route` | `score(candidate, P)` | `-> ScoreResult` | `route(demand, candidates, score)` picks best eligible |
| `bound` | `bounds(telemetry, P)` | `-> list[dimension]` | `bound(dimensions)` merges by severity |

`P` carries `{"demand": ...}` on the route stage (so thresholds can depend on the demand).

Every function is **pure**: no clock, no network, no randomness, no side effects
(see DETERMINISM.md). Build results with the helpers in `routestra_packs._base`.

### route: `score(candidate, P) -> ScoreResult`

Use the kernel `score` helper: it takes a domain value function + thresholds + an evidence field.

```python
from ._base import score as kscore

def _value(c):
    return c["capacity"] * (c["quality_pct"] / 100)

def score(candidate, P=None):
    max_latency = (P or {}).get("demand", {}).get("max_latency_ms", 200)
    return kscore(candidate, _value,
                  thresholds={"quality_pct": {"min": 50}, "latency_ms": {"max": max_latency}},
                  evidence_field="verified")   # candidate[evidence_field] must be truthy
```

`thresholds`: `{field: {"min": x} | {"max": y} | {"eq": v}}`. A ScoreResult is
`{name, score, eligible, verified, reason}` — ineligible candidates are excluded from routing.

### bound: `bounds(telemetry, P) -> list[dimension]`

```python
from ._base import compliant, restricted, violation

def bounds(telemetry, P=None):
    dims = []
    if telemetry["load"] > telemetry["limit"]:
        dims.append(violation("load", "over limit"))
    elif telemetry["load"] > telemetry["limit"] * 0.9:
        dims.append(restricted("load", "near limit"))
    else:
        dims.append(compliant("load"))
    return dims
```

The kernel merges dimensions to the highest severity (`violation > restricted > compliant`).
That severity aligns with Attestra (`compliant/restricted/violation -> valid/thin/breach`).

## SAMPLES

```python
SAMPLES = {
    "route": {"demand": {"max_latency_ms": 150},
              "candidates": [{"name": "A", "capacity": 100, "quality_pct": 80,
                              "latency_ms": 100, "verified": True, "evidence_hash": "hA"}]},
    # or, for a bound pack:
    "bound": {"telemetry": {"load": 80, "limit": 100}},
}
```

## Checklist

- [ ] Module exposes `MANIFEST`, the stage functions for its `stages`, and `SAMPLES`
- [ ] `candidate_schema` file exists (else the loader reports an error and drops the pack)
- [ ] Each stage function is pure (no clock/network/random/side effects)
- [ ] route packs return ineligible ScoreResults for candidates that fail thresholds/evidence
- [ ] `python cli.py pack` shows the pack with 0 errors; `determinism` stays clean
