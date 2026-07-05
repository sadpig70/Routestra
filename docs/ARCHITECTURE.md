# Routestra Architecture

> **One deterministic routing kernel + N domain packs.** Routestra scores candidate
> resource-sources against multi-dimensional constraints + evidence, routes a demand to
> the best eligible one, bounds allocations against thresholds, and verifies provenance —
> all deterministically, appending to a hash-chained routing ledger.

## Layers

```
   cli.py           routestra_run.py (RouteRun: score->route->bound->verify->ledger)
   (subcommands)    ── meta / IO layer (file I/O, injected `now`) ──
                                  │ calls
   ┌────────────────── routestra_packs/ (federated domain packs) ──────────────────┐
   loader.py (discover · validate stages · candidate_schema · fingerprint dedup · run_stage)
   compute-power(ref) · power-roam · inference-grid · watt-fabric · soil-carbon      (route)
   thermal-cascade(ref) · thermal-plume · waste-stack · season-battery · climate-resilience (bound)
   └────────────────────────────────────────────────────────────────────────────────┘
                                  │ each pack contributes formulas only
   ┌────────────────── routestra_core/ (deterministic kernel) ─────────────────────┐
   candidate · score · route · bound · verdict · provenance · ledger · fingerprint · determinism
                        (stdlib only; no clock/network/AI; `now` injected)
   └────────────────────────────────────────────────────────────────────────────────┘
```

- **Kernel (`routestra_core/`)** — single source of truth. Scoring eligibility, routing
  selection, severity-merged bound verdicts, provenance, and the ledger are defined **once** here.
- **Packs (`routestra_packs/`)** — each pack is one corpus project projected as domain formulas:
  `score(candidate, P)` (route) and/or `bounds(telemetry, P)` (bound). Federated (`source_project`).
- **Meta/IO** — CLI + RouteRun pipeline. File I/O + injected `now`, still clock-free.

## The stages (`routestra_run.route_run`)

```
score -> pack score_fn assigns a value; kernel applies thresholds + evidence -> eligible?
route -> route(demand, candidates, score) picks the highest-score eligible candidate
bound -> bound(dimensions) merges pack dimension verdicts (violation > restricted > compliant)
verify-> verify_provenance(plan, chain): the selected candidate's evidence must be confirmed
                              │
                              └─> append_routing (hash-chain routing ledger)
```

## Grounded in real corpus code

| Kernel piece | Real code it generalizes |
|---|---|
| `score` | `SkyGrid.evaluate_power_availability` (grid·renewable·latency_penalty; renewable≥50 + satellite) |
| `route` | `SkyGrid.plan_compute_roaming` (best eligible, rejection reasons) |
| `bound` | `ThermalCascadeBound.evaluate_site` (power/thermal vs threshold, severity merge) |
| `verify_provenance` | `SkyGrid.verify_provenance` (selected evidence in confirmed chain) |

`compute-power` is the route reference (SkyGrid parity); `thermal-cascade` the bound reference.

## -stra platform family

Routestra is the third of the HELIX-derived `-stra` family. All three are deterministic
kernels + plugins that **share the severity algebra**:

| Platform | verb | severity |
|---|---|---|
| [Attestra](https://github.com/sadpig70/Attestra) | attest | valid < thin < breach |
| [Clearstra](https://github.com/sadpig70/Clearstra) | clear | (clearing verdicts) |
| **Routestra** | route | compliant < restricted < violation |

`routestra_core.verdict.to_attestra_verdict` maps `compliant/restricted/violation ->
valid/thin/breach`, so a routing bound decision can be attested by Attestra.

## Determinism boundary

See [DETERMINISM.md](DETERMINISM.md). Kernel + pack formulas are pure stdlib with injected
`now`; `routestra_core/determinism.py` enforces it (`routestra determinism` → clean).

## Extending

See [PACK-CONTRACT.md](PACK-CONTRACT.md) — a new pack is a manifest + stage functions +
candidate schema, with **no kernel change**.
