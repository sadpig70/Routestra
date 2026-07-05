#!/usr/bin/env bash
# Deterministic full smoke: unittest + determinism + routing pipeline + ledger.
# One command, injected `now`, no wall clock.
#
# Usage: scripts/smoke.sh [NOW]     (NOW default 2026-07-05)
set -euo pipefail
cd "$(dirname "$0")/.."
NOW="${1:-2026-07-05}"
TMP=".smoke_tmp"
cleanup() { rm -rf "$TMP"; }
trap cleanup EXIT
rm -rf "$TMP"; mkdir -p "$TMP"

echo "[1/5] unittest"
python -m unittest discover -s tests -q

echo "[2/5] determinism boundary"
python cli.py determinism >/dev/null && echo "      clean"

echo "[3/5] route pipeline (compute-power) + provenance + ledger"
echo '[{"evidence_hash":"hB","confirmed":true}]' > "$TMP/chain.json"
python cli.py run --pack compute-power --chain "$TMP/chain.json" --ledger "$TMP/r.jsonl" \
  --subject CP --now "$NOW" >/dev/null
python cli.py verify --ledger "$TMP/r.jsonl" >/dev/null && echo "      routing ledger chain valid"

echo "[4/5] bound pipeline (thermal-cascade)"
python cli.py run --pack thermal-cascade --ledger "$TMP/t.jsonl" --now "$NOW" >/dev/null
python cli.py verify --ledger "$TMP/t.jsonl" >/dev/null && echo "      bound ledger chain valid"

echo "[5/5] pack registry"
python -c "from routestra_packs.loader import load_packs; r=load_packs(); assert len(r['packs'])==10 and not r['errors'], r; print('      10 packs, 0 errors')"

echo "SMOKE OK"
