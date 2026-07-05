# WORKPLAN-Routestra — 실행 계획 (PGF plan)

> DESIGN-Routestra.md + DESIGN-RoutestraPacks.md → 실행 가능한 작업 계획.
> POLICY + 노드 위상정렬 + 검증 게이트. 이 저장소만으로 자립 구동(독립 repo). -stra 3형제 완성.

## POLICY

```yaml
POLICY:
  max_verify_cycles: 2
  stdlib_only: true               # HELIX/Attestra/Clearstra CI 철학 계승
  determinism: strict             # 커널·팩 시계/네트워크/AI 금지 (now 주입)
  federate_not_fuse: true         # 원본 도메인 복사·포크 금지 — 공식 계약만 적재
  single_source_of_truth: true    # score/route/bound/provenance/ledger 커널에 1회만
  reference_pack_parity: true     # ComputePowerPack == SkyGrid evaluate/plan/verify
  verdict_aligned: true           # bound severity(compliant/restricted/violation) = Attestra severity
  on_blocked: skip_and_continue
  completion: all_done_or_blocked
```

## 노드 순서 (의존 위상정렬)

```text
# ── Phase 1: 커널 (RoutestraCore) ──
1.  Candidate      — 후보/telemetry 모델 + 검증
2.  Score          @dep:1 — 후보 채점 + eligibility (SkyGrid.evaluate 계승)
3.  Route          @dep:2 — 최적 eligible 라우팅 (SkyGrid.plan 계승)
4.  Bound          — 다차원 임계 verdict 병합 (ThermalCascadeBound 계승)
5.  Verdict        — severity 대수 (compliant<restricted<violation)
6.  Provenance     @dep:3 — 증거 chain 검증 (SkyGrid.verify 계승)
7.  Ledger         — hash-chain 라우팅 원장 (Attestra 규율)
8.  Fingerprint    — 팩 dedup primitive
9.  Determinism    @dep:3,4 — stdlib·주입 경계 검증기

# ── Phase 2: 팩 계약 (PackContract) ──
10. PackManifest   @dep:1 — {name,version,stages,candidate_schema,source_project}
11. PackAPI        @dep:2,4 — score/bounds 계약
12. PackLoader     @dep:10,8 — 발견·로드·stages검증·dedup·candidate_schema 강제
13. PackRegistry   @dep:12 — 레지스트리 + lookup

# ── Phase 3: 팩 (Packs) — 레퍼런스 우선 ──
14. ComputePowerPack @dep:11 — 레퍼런스 (SkyGrid parity, route)
15. ThermalCascadePack @dep:11 — bound 레퍼런스 (ThermalCascadeBound parity)
16. Packs[나머지 8종] @dep:14,15 — PowerRoam/InferenceGrid/WattFabric/SoilCarbon/
                                  ThermalPlume/WasteStack/SeasonBattery/ClimateResilience
                                  [parallel] — 계약 동일, 독립 포팅

# ── Phase 4: 합성 · 인터페이스 ──
17. RouteRun       @dep:3,4,6,7 — score→route→bound→verify→ledger 파이프라인
18. Schemas        @dep:1,3,4,7,10 — JSON Schema (candidate/route-plan/bound-verdict/ledger/manifest)
19. CLI            @dep:13,17 — sample/score/route/bound/verify/report/pack
20. Docs           @dep:9 — README/ARCHITECTURE/PACK-CONTRACT/DETERMINISM

# ── Phase 5: 검증 ──
21. Tests          @dep:14,15,17 — 커널 + 팩 parity + 파이프라인 unittest
22. VERIFY         @dep:21 — 3관점 (acceptance/quality/architecture)
```

## 검증 게이트

```text
- 커널·팩 전부 stdlib import만 (외부 패키지 0)
- 커널·팩 전부 now 주입식 (Date.now·random·socket 호출 0); hash에서 now/*_at 제외
- ★ reference_pack_parity: ComputePowerPack score/route/verify == 원본 SkyGrid (샘플 다수)
- ★ ThermalCascadePack bound == 원본 ThermalCascadeBound.evaluate_site verdict
- ★ verdict_aligned: bound severity 매핑(compliant→valid/restricted→thin/violation→breach) 검증
- PackLoader dedup + candidate_schema 강제
- unittest green + Determinism 검증기 PASS
- 3관점: acceptance · quality(커널/팩 중복 0) · architecture(federate 유지)
```

## 페이즈 전이

```text
Phase1 → Phase2: 커널 9노드 done + Determinism PASS
Phase2 → Phase3: PackAPI 계약 확정 + PackRegistry 동작
Phase3 → Phase4: ComputePowerPack parity + ThermalCascadePack parity (레퍼런스 선행)
Phase4 → Phase5: 모든 노드 terminal
Phase5 → 완료: VERIFY passed (rework ≤ max_verify_cycles)
```
