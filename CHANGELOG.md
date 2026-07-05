# Changelog

All notable changes to Routestra are documented here. Dates are ISO-8601.

## [0.1.0] — 2026-07-05

First release of Routestra — a deterministic resource-routing platform: one stdlib
kernel + N domain packs. Third of the HELIX-derived `-stra` family alongside
[Attestra](https://github.com/sadpig70/Attestra) (attest) and
[Clearstra](https://github.com/sadpig70/Clearstra) (clear).

### Kernel (`routestra_core/`)
- Candidate/telemetry model + validation (`candidate.py`)
- Scoring — value + threshold/evidence eligibility, SkyGrid parity (`score.py`)
- Routing — best-eligible selection, deterministic tie-break, SkyGrid parity (`route.py`)
- Bounding — severity-merged verdict (compliant/restricted/violation), ThermalCascadeBound
  parity (`bound.py`)
- Verdict severity + Attestra alignment (`verdict.py`)
- Provenance verification, SkyGrid parity (`provenance.py`)
- Hash-chained, time-independent, tamper-evident routing ledger (`ledger.py`)
- Pack fingerprint / dedup (`fingerprint.py`), determinism checker (`determinism.py`)

### Packs (`routestra_packs/`) — 10, all zero-kernel-change
- route: compute-power (reference, SkyGrid parity), power-roam, inference-grid,
  watt-fabric, soil-carbon
- bound: thermal-cascade (reference, ThermalCascadeBound parity), thermal-plume,
  waste-stack, season-battery, climate-resilience

### Orchestration, interface, docs
- `routestra_run.py` — RouteRun pipeline (score → route → bound → verify → ledger)
- `cli.py` — `pack / run / stage / verify / determinism`
- 14 schemas (10 candidate + 4 kernel); loader enforces `candidate_schema` existence
- `docs/ARCHITECTURE.md`, `docs/PACK-CONTRACT.md`, `docs/DETERMINISM.md`

### Guarantees
- Determinism boundary enforced (`routestra determinism` → clean)
- Verdict severity aligns with Attestra (`compliant/restricted/violation ->
  valid/thin/breach`), so a routing decision can be attested by the -stra family
- Full test suite green (`python -m unittest discover -s tests`) — 45 tests
