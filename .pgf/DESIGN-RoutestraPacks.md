# RoutestraPacks Design @v:0.1

> `DESIGN-Routestra.md`의 `Packs` 노드 `(decomposed)` 분리 트리. 1차 도메인 팩 = HELIX corpus의
> **자원-라우팅 군집**을 `PackContract`로 투영. 각 팩은 `stages`(route/bound 중 구현분)와 도메인
> 공식(채점·임계)만 기여하며 커널 로직을 재정의하지 않는다.
> **레퍼런스**: `compute-power`(SkyGrid evaluate/plan/verify parity).

---

## 1. Gantree — 1차 도메인 팩 (10종)

```
RoutestraPacks // 1차 도메인 팩 (resource-routing cluster) (designing) @v:0.1
    ComputePowerPack // compute→최저탄소 전력 라우팅 (route) — 레퍼런스 (designing) #reference
    PowerRoamPack // 모바일 compute가 최저가 전력으로 로밍 (route) (designing)
    InferenceGridPack // AI 추론 수요를 그리드 primitive로 라우팅 (route) (designing)
    WattFabricPack // AI 워크로드를 cost/carbon/latency/sovereignty로 라우팅 (route) (designing)
    SoilCarbonPack // 재생 자금을 최고영향 농지로 라우팅 (route) (designing)
    ThermalCascadePack // 전력+열 방출을 그리드·생태 임계 내로 (bound) (designing)
    ThermalPlumePack // 해양 열배출 분산 배치 (bound) (designing)
    WasteStackPack // 좌초 DC 사이트 이중 현금흐름 임계 (bound) (designing)
    SeasonBatteryPack // DAC-as-energy 저장 사이트 (bound) (designing)
    ClimateResiliencePack // 자산 기후 회복력 스코어링 (bound) (designing)
```

> depth ≤ 2 유지 — 각 팩의 stages + 공식은 노드 아래 간략 PPR(`#`)로. 커널 계약이
> `score/bounds`를 고정하므로 팩은 stages와 공식만 명세하면 된다.

---

## 2. 팩별 명세 (간략 PPR — 실코드 근거는 [실코드])

### ComputePowerPack — 레퍼런스 (source: SkyGrid = WattMesh+OrbiRoam+PowerRoam) [실코드]

```
ComputePowerPack // compute→최저탄소 전력 라우팅 (designing) #reference
    # source_project: github.com/sadpig70/SkyGrid
    # stages: route
    # score:  grid_capacity_mw * (renewable_pct/100) * max(0, 1 - latency_ms/200)   [실코드]
    # thresholds: renewable_pct >= 50 AND latency_ms <= demand.max_latency_ms
    # evidence:   satellite_attestation.confirmed_renewable == True                 [실코드]
    # criteria: score/route/verify 결과가 SkyGrid evaluate_power_availability/plan_compute_roaming/
    #           verify_provenance와 동일 (parity)
```

### PowerRoamPack (source: PowerRoam)

```
PowerRoamPack // 모바일 compute 최저가 전력 로밍 (designing)
    # source_project: github.com/sadpig70/PowerRoam
    # stages: route
    # score: power_availability / power_cost  (저가·가용 우선); 제약: comm_latency <= budget
```

### InferenceGridPack (source: InferMesh)

```
InferenceGridPack // AI 추론 수요를 그리드 primitive로 (designing)
    # source_project: github.com/sadpig70/InferMesh
    # stages: route
    # score: available_tflops * (renewable_pct/100) / marginal_grid_cost
```

### WattFabricPack (source: WattWeaveAI / WattMesh)

```
WattFabricPack // AI 워크로드 다기준 라우팅 (designing)
    # source_project: github.com/sadpig70/WattWeaveAI
    # stages: route
    # score: weighted(cost, carbon, latency, sovereignty, chip_availability)  (가중합 정규화)
    # thresholds: sovereignty_ok AND chip_available
```

### SoilCarbonPack (source: SoilBond + FieldRoot) [실코드]

```
SoilCarbonPack // 재생 자금을 최고영향 농지로 (designing)
    # source_project: github.com/sadpig70/SoilBond
    # stages: route
    # score: soil_carbon_reduction * resilience_score  (검증 감축량 * 회복력)
    # thresholds: verifiable_reduction == True
```

### ThermalCascadePack — bound 레퍼런스 (source: ThermalCascadeBound) [실코드]

```
ThermalCascadePack // 전력+열 방출 임계 판정 (designing)
    # source_project: github.com/sadpig70/ThermalCascadeBound
    # stages: bound
    # bounds: [power dimension vs grid threshold, thermal dimension vs ecological dispersion threshold]
    #         각 차원 verdict compliant/restricted/violation → 커널 bound() 병합       [실코드]
```

### ThermalPlumePack (source: ThermalPlumeStage)

```
ThermalPlumePack // 해양 열배출 분산 배치 (designing)
    # source_project: github.com/sadpig70/ThermalPlumeStage
    # stages: bound
    # bounds: [dilution window vs ecological threshold, discharge temp vs limit] → verdict
```

### WasteStackPack (source: WasteStack)

```
WasteStackPack // 좌초 DC 이중 현금흐름 임계 (designing)
    # source_project: github.com/sadpig70/WasteStack
    # stages: bound
    # bounds: [grid interconnect capacity, low-grade heat offtake] → compliant/restricted/violation
```

### SeasonBatteryPack (source: SeasonBat)

```
SeasonBatteryPack // DAC-as-energy 저장 사이트 (designing)
    # source_project: github.com/sadpig70/SeasonBat
    # stages: bound
    # bounds: [firm power draw vs supply, storage cycle vs capacity] → verdict
```

### ClimateResiliencePack (source: ClimateMesh)

```
ClimateResiliencePack // 자산 기후 회복력 스코어링 (designing)
    # source_project: github.com/sadpig70/ClimateMesh
    # stages: bound
    # bounds: [threat, inherent_risk, controls, residual_risk] → residual >= limit ? violation : compliant
```

---

## 3. 팩 확장 규칙 & 2차 파도

```text
PackExpansionRule
    SameContract // score/bounds 준수하면 팩 추가 = 매니페스트 + 공식 파일만
    NoKernelChange // 커널 수정 없이 팩 등록 (플랫폼성의 증거)
    StagesDeclared // stages(route/bound)로 구현 단계 명시
    DedupByFingerprint // 중복 재조합 팩은 PackLoader가 거부
    VerdictAligned // bound 팩 verdict = Attestra severity 동형 (생태계 조합)
```

2차 파도 후보(동일 계약): `EnerGrid`·`SovMesh`(주권 라우팅)·`FieldRoot`(농지 라우팅 단독). 순수 verdict/청산
군집은 Attestra/Clearstra 소관.
