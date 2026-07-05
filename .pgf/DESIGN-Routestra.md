# Routestra Design @v:0.1

> PGF design mode 산출. **Routestra = 다차원 물리 제약(재생%·지연·그리드용량·열분산·생태한계) 하에서
> 자원(컴퓨트·전력·열·자금)을 최적 위치로 라우팅/배치하고, 임계-bounded verdict + 증거-verified
> provenance를 내는 결정론 라우팅 플랫폼.** HELIX corpus의 자원-라우팅 군집(SkyGrid·PowerRoam·
> InferMesh·ThermalCascadeBound·ThermalPlumeStage·WasteStack·SeasonBat·WattWeaveAI·SoilBond·
> ClimateMesh)이 도메인만 다를 뿐 **동일한 기계**(`score → route → bound → verify` + 라우팅 원장)를
> 반복한다는 관찰에서 출발한다. Routestra는 그 기계를 **커널(routestra-core)** 로 한 번만 정의하고, 각
> 도메인을 **라우팅 팩(routing pack)** 으로 얹는다. 계보: HELIX → Routestra (자식 저장소, 독립 구동).
>
> **★ -stra 패밀리:** Attestra(attest·증언) · Clearstra(clear·청산) · **Routestra(route·라우팅)**.
> 세 플랫폼은 verdict severity 대수(valid/thin/breach ≅ compliant/restricted/violation)를 공유해
> 상호 조합 가능하다(Routestra bound verdict → Attestra 증언).

---

## 0. 핵심 명제

> **하나의 결정론 라우팅 커널 + N개 도메인 팩.** corpus의 각 도메인(compute-power·thermal-cascade·
> inference-grid…)은 "후보 자원-소스를 다차원 제약·증거로 채점 → 제한 수요를 최적 위치로 라우팅 →
> 임계 내 여부를 verdict로 판정 → provenance 검증"이라는 **같은 substrate**를 도메인 공식만 바꿔
> 재구현한 것이다. Routestra는 그 substrate를 단일 출처로 승격하고, 팩은 도메인 공식(채점·임계)만 기여한다.

설계 원칙 (Attestra/Clearstra 계승):
1. **커널 단일 출처** — score/route/bound/provenance/ledger는 `routestra-core`에 한 번만.
2. **팩은 연합(federate)** — 각 도메인은 원본 저장소(github.com/sadpig70/*)에 그대로, 채점/임계 계약만 적재.
3. **결정론 경계** — 커널·팩 함수는 순수 stdlib(시계·네트워크·AI 없음). 시간은 주입(`now`). 채점·라우팅·bound는
   전부 결정론이라 경계와 자연 정합.
4. **verdict 정렬** — bound verdict(compliant<restricted<violation)는 Attestra severity와 동형 → 생태계 조합.

---

## 1. HELIX 라우팅 기계 → Routestra 매핑 (실코드 근거)

| corpus 반복 요소 (실코드) | Routestra 커널 요소 | 결정론 클래스 |
|---|---|---|
| `SkyGrid.evaluate_power_availability` (score = capacity·renewable·latency_penalty) | **Score** — 후보 채점 | 순수 결정론 |
| `SkyGrid.plan_compute_roaming` (최적 eligible 선택 + rejection reasons) | **Route** — 최적 라우팅 | 순수 결정론 |
| `ThermalCascadeBound.evaluate_site` (power/thermal vs threshold → severity 병합) | **Bound** — 임계 verdict | 순수 결정론 |
| `SkyGrid.verify_provenance` (선택 tasking/evidence가 confirmed chain에 존재) | **Provenance** — 증거 검증 | 순수 결정론 |
| compliant/restricted/violation 병합 | **Verdict** — severity 대수 | 순수 결정론 |
| 각 도메인의 라우팅/판정 기록 | **Ledger** — hash-chain 라우팅 원장 | 순수 결정론 (now 주입) |

> 3-플랫폼 위상: Attestra=verdict(증언), Clearstra=allocation(청산), Routestra=placement(라우팅).
> 셋 다 결정론 커널 + 플러그인, severity 대수 공유.

---

## 2. Gantree — Routestra 구조

```
Routestra // 결정론 자원 라우팅/배치 플랫폼 (designing) @v:0.1
    RoutestraCore // 커널 — 단일 출처 결정론 라우팅 substrate (designing) #core
        Candidate // 후보 자원-소스/사이트 모델 + 검증 (designing) #core
        Score // 후보를 제약·증거로 채점 (score·eligible·reason) (designing) @dep:Candidate #core
        Route // 제한 수요를 최적 eligible 후보로 라우팅 (designing) @dep:Score #core
        Bound // 다차원 임계 verdict (compliant/restricted/violation) (designing) #core
        Verdict // severity 대수 (compliant<restricted<violation ≅ Attestra) (designing) #core
        Provenance // 라우팅 계획을 증거 chain에 대해 검증 (designing) @dep:Route #core
        Ledger // hash-chain 라우팅 원장 (designing) #core
        Fingerprint // 라우팅 팩 dedup primitive (designing) #core
        Determinism // stdlib·now/sim 주입 경계 검증기 (designing) #core
    PackContract // 라우팅 팩 확장 규격 (designing) @dep:RoutestraCore #contract
        PackManifest // {name,version,stages,candidate_schema,source_project} (designing) #contract
        PackAPI // score/bounds 시그니처 (stages별) (designing) @dep:RoutestraCore #contract
        PackLoader // 발견·로드·stages검증·dedup (designing) @dep:PackManifest #contract
        PackRegistry // 등록된 팩 레지스트리 + lookup (designing) @dep:PackLoader #contract
    Packs // 1차 도메인 팩 — see DESIGN-RoutestraPacks.md (decomposed) @dep:PackContract #packs
    RouteRun // 파이프라인 score→route→bound→verify→ledger (designing) @dep:Route,Bound,Provenance,Ledger #pipeline
    CLI // sample/score/route/bound/verify/report/pack (designing) @dep:RoutestraCore,PackRegistry #cli
    Schemas // JSON Schema (candidate/route-plan/bound-verdict/ledger/manifest) (designing) #schema
    Docs // README/ARCHITECTURE/PACK-CONTRACT/DETERMINISM (designing) #docs
    Tests // 결정론 unittest (커널 + 팩 + 파이프라인) (designing) @dep:RoutestraCore,Packs #test
```

> `Packs`는 6레벨 진입 회피 + 도메인별 공식 상세를 위해 `DESIGN-RoutestraPacks.md`로 분리(`(decomposed)`).

---

## 3. PPR — 커널 핵심 함수 (계약)

### 3.1 Score — 후보 채점 (SkyGrid.evaluate_power_availability 일반화)

```python
def score(candidate: dict, thresholds: dict, evidence: dict, score_fn) -> dict:
    """후보를 도메인 채점식으로 평가하고 임계·증거로 eligibility 판정.
       score_fn(candidate) -> float 은 팩 제공 (예: capacity * renewable/100 * latency_penalty)."""
    value = score_fn(candidate)                              # 팩 도메인 채점
    met, reason = check_thresholds(candidate, thresholds)   # 결정론 임계 검사
    verified = evidence_verified(candidate, evidence)        # 증거 확인 (예: 위성 confirmed)
    eligible = met and verified
    return {"candidate": candidate.get("name",""), "score": value,
            "eligible": eligible, "verified": verified,
            "reason": "" if eligible else (reason or "evidence_not_verified")}
    # acceptance_criteria (SkyGrid 계승):
    #   - eligible = 모든 임계 충족 AND 증거 verified
    #   - 결정론: 동일 candidate/thresholds/evidence → 동일 score·eligible
```

### 3.2 Route — 최적 라우팅 (SkyGrid.plan_compute_roaming 일반화)

```python
def route(demand: dict, candidates: list, score_fn, thresholds: dict, now: str) -> dict:
    """제한 수요를 최고 score의 eligible 후보로 라우팅. rejection reason 기록."""
    scored = [score(c, thresholds, c.get("evidence",{}), score_fn) for c in candidates]
    eligible = [s for s in scored if s["eligible"]]
    best = max(eligible, key=lambda s: s["score"]) if eligible else None   # 결정론 tie-break by name
    return {"selected": best["candidate"] if best else None,
            "selected_score": best["score"] if best else 0.0,
            "all_scores": scored, "demand": demand, "routed_at": now}
    # acceptance_criteria:
    #   - eligible 없으면 selected=None (SkyGrid best is None 계승)
    #   - 최고 score eligible 선택, 동점은 이름 오름차순(결정론)
    #   - 각 후보 rejection_reason 노출
```

### 3.3 Bound — 다차원 임계 verdict (ThermalCascadeBound.evaluate_site 일반화)

```python
SEVERITY = {"compliant": 0, "restricted": 1, "violation": 2}   # ≅ Attestra valid<thin<breach

def bound(dimensions: list) -> dict:
    """차원별 verdict를 최고 severity로 병합 (ThermalCascadeBound 계승).
       dimensions = [{dimension, verdict, reason}] (팩 bounds()가 생성)."""
    if not dimensions:
        return {"verdict": "restricted", "reason": "no_dimensions", "worst": None}
    worst = max(dimensions, key=lambda d: SEVERITY[d["verdict"]])
    return {"verdict": worst["verdict"], "reason": worst["reason"],
            "worst": worst["dimension"], "dimensions": dimensions}
    # acceptance_criteria:
    #   - 병합 verdict = 차원 중 최고 severity (violation > restricted > compliant)
    #   - 결정론: 순수 max
```

### 3.4 Provenance — 증거 검증 (SkyGrid.verify_provenance 일반화)

```python
def verify_provenance(plan: dict, chain: list) -> dict:
    """라우팅 계획의 선택 후보 증거가 confirmed evidence chain에 존재하는지 검증."""
    sel = plan.get("selected")
    ev = plan.get("selected_evidence")
    link = next((l for l in chain if l.get("evidence_hash") == ev and l.get("confirmed")), None)
    return {"provenance_valid": sel is not None and link is not None,
            "chain_length": len(chain), "selected": sel}
    # acceptance_criteria: 선택 존재 AND confirmed link 존재 → valid (SkyGrid 계승)
```

### 3.5 Ledger — hash-chain 라우팅 원장 (Attestra/Clearstra 규율 계승)

```python
def append_routing(ledger_path: str, result: dict, pack: str, kind: str, now: str) -> dict:
    """route/bound/verify 결과를 hash-chain 레코드로 append.
       record_hash = sha256(canonical(record − {record_hash, recorded_at})) → 시간독립."""
    # acceptance_criteria: 체인 무결성 verify + 변조 탐지 + now 메타 제외 (Attestra와 동형)
```

### 3.6 PackContract — 라우팅 팩 확장 규격

```python
PackManifest = dict = {
    "name": str, "version": str,
    "stages": list[str],          # subset: ["route","bound"]  (verify는 커널 유틸)
    "candidate_schema": str,      # 이 도메인의 후보/telemetry 스키마
    "source_project": str,        # github.com/sadpig70/*
}

# stages별 팩 제공 순수 함수:
def score(candidate: dict, P: dict) -> float          # route stage — 후보 채점식
def bounds(telemetry: dict, P: dict) -> list[dict]    # bound stage — [{dimension,verdict,reason}]

def load_packs(pack_dir, seen_fp) -> dict:
    """라우팅 팩 발견·검증·dedup. stages별 필요한 함수 존재 검증, candidate_schema 존재 강제."""
    # acceptance_criteria: fingerprint 충돌 거부, stages 함수 검증, 결정론
```

---

## 4. 결정론 경계 (지배 제약)

```text
RoutestraCore + PackContract → 순수 결정론 (stdlib only, 시계/네트워크/AI 없음)
  - 시간은 주입(now), hash 입력에서 now/*_at 제외 → 시간 무관 재현
팩 함수(score/bounds) → 순수 결정론 (부작용 금지)
도메인 예측·시세·위성 피드 등 → 메타층 (Routestra 경계 밖 — 후보/telemetry를 *생산*)
```

---

## 5. 완료 기준 (acceptance)

```text
RoutestraAcceptance
    SingleSourceKernel // score/route/bound/provenance/ledger를 커널에 1회만 정의 (팩 중복 0)
    PackContractStable // score/bounds 계약으로 도메인 팩 무한 확장
    ReferencePackPorted // ComputePowerPack이 SkyGrid evaluate/plan/verify 재현 (parity)
    VerdictAligned // bound severity(compliant/restricted/violation) = Attestra severity 동형
    DeterministicCore // 커널·팩 전부 stdlib·주입식·시계 없음
    Federated // 팩은 도메인 공식 계약만 적재 (복사 아님, source_project 태그)
    Tested // 커널 unittest green + 팩 route/bound 검증
```
