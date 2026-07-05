# Routestra Determinism Boundary

> Routestra's scores, routes, and verdicts must be **reproducible**: the same input yields
> the same output on any machine, at any time. Enforced by a checker.

## The rule

**`routestra_core/` and `routestra_packs/` are pure stdlib and fully deterministic.** They must not:

- read the clock (`time.time`, `datetime.now`, `datetime.utcnow`, `date.today`, …)
- use randomness (`random`, `secrets`)
- touch the network (`socket`, `requests`, `urllib`, `http`, …)
- depend on any non-stdlib package

`math` **is** allowed (deterministic).

Time is **injected** as `now` (a string), appears only as metadata (`routed_at`,
`recorded_at`), and is **excluded from every hash**. So a routing decision computed at two
different times is byte-identical.

## Determinism of routing itself

`route(demand, candidates, score_fn)` ranks eligible candidates by `(-score, str(name))`, so
ties break reproducibly. Same demand + candidates → same selection, always. Ledger records hash
their content minus wall-time metadata:

```
record_hash = sha256(canonical_json(record − {record_hash, recorded_at}))
```

Re-running with a different `now` produces identical `record_hash` values (tested).

## The checker

`routestra_core/determinism.py` walks the AST of every `.py` under `routestra_core/` and
`routestra_packs/` and flags forbidden imports/calls.

```bash
python cli.py determinism        # -> {"clean": true, "files_scanned": N, "violations": {}}
```

`clean: true` is a release gate.

## Layer boundaries

| Layer | Files | Rule |
|---|---|---|
| **Kernel** | `routestra_core/*` | pure stdlib, deterministic, `now` injected — **scanned** |
| **Packs** | `routestra_packs/*` | pure formulas, deterministic — **scanned** |
| **Meta / IO** | `cli.py`, `routestra_run.py` | file I/O + injected `now`; still clock-free — not scanned |
| **Domain feed** | the pack's source project (satellite tasking, price/forecast feeds) | **outside** the boundary — produces the candidate/telemetry |

Non-determinism (a satellite feed, a demand forecast, a market price) legitimately lives in the
domain feed that *builds the candidate/telemetry*. It runs before Routestra. Routestra's job —
candidate to score to route/bound to verdict — is the deterministic part.
