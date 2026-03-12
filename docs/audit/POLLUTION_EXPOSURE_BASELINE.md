Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Pollution Exposure Baseline

Status: BASELINE (POLL-2)  
Date: 2026-03-05  
Scope: deterministic exposure accumulation, health-risk stub thresholds, diegetic measurement artifacts, institutional compliance reporting via SIG, explain integration, and proof/replay hooks.

## 1) Exposure Model and Thresholds

Authoritative exposure remains process-mediated and deterministic:

- exposure increments derive from local concentration sampling per subject/pollutant in sorted order.
- threshold evaluation emits canonical health-risk events (`warning`, `critical`) and hazard hook rows (`hazard.health_risk_stub`).
- thresholds are registry-driven through `data/registries/exposure_threshold_registry.json`.

Primary surfaces:

- `src/pollution/exposure_engine.py`
- `tools/xstack/sessionx/process_runtime.py` (`process.pollution_dispersion_tick`)
- `schema/pollution/exposure_threshold.schema`
- `schema/pollution/health_risk_event.schema`

## 2) Measurement Workflow

Diegetic measurement runs through `process.pollution_measure`:

- validates registered pollutant + optional sensor type.
- samples local concentration by `spatial_scope_id`.
- emits canonical measurement rows (`pollution_measurement_rows`).
- produces OBSERVATION info artifacts (`artifact.pollution.measurement`).
- emits deterministic `knowledge_receipt_rows` for epistemic gating.

Primary surfaces:

- `src/pollution/measurement_engine.py`
- `schema/pollution/pollution_measurement.schema`
- `data/registries/pollution_sensor_type_registry.json`

## 3) Compliance Reporting Workflow

Institutional compliance hook runs through `process.pollution_compliance_tick`:

- computes deterministic `avg|max` region statistics from concentration fields.
- compares against threshold policy and classifies `ok|warning|violation`.
- emits REPORT artifacts (`artifact.pollution.compliance_report`).
- dispatches via SIG channel when available; deterministic degrade decision when unavailable.

Primary surfaces:

- `src/pollution/compliance_engine.py`
- `schema/pollution/compliance_report.schema`
- `tools/xstack/sessionx/process_runtime.py`

## 4) Enforcement and Explainability

POLL-2 enforcement additions:

- RepoX invariants:
  - `INV-EXPOSURE-PROCESS-ONLY`
  - `INV-NO-OMNISCIENT-POLLUTION-KNOWLEDGE`
  - `INV-COMPLIANCE-REPORT-ARTIFACT`
- AuditX smells:
  - `DirectExposureWriteSmell` (`E254_DIRECT_EXPOSURE_WRITE_SMELL`)
  - `OmniscientPollutionUILeakSmell` (`E255_OMNISCIENT_POLLUTION_UI_LEAK_SMELL`)

Explain integration:

- `explain.exposure_threshold`
- `explain.compliance_violation`

## 5) Proof and Replay

Proof surface now includes:

- `pollution_exposure_hash_chain`
- `pollution_health_risk_hash_chain`
- `pollution_measurement_hash_chain`
- `pollution_compliance_report_hash_chain`

Replay verifier:

- `tools/pollution/tool_replay_exposure_window.py`

## 6) Gate Execution

Validation level executed: STRICT governance checks + POLL-2 targeted TestX.

- topology map updated:  
  `py -3 tools/governance/tool_topology_generate.py --repo-root . --out-json docs/audit/TOPOLOGY_MAP.json --out-md docs/audit/TOPOLOGY_MAP.md`  
  - result: `complete`  
  - deterministic_fingerprint: `906cd81dd787b51e245563e5dde1482746e997a6ccfef686fccfcfa9c2958bd8`

- RepoX STRICT:  
  `py -3 tools/xstack/repox/check.py --repo-root . --profile STRICT`  
  - result: `pass` (`findings=17`, warnings only)

- AuditX STRICT:  
  `py -3 tools/xstack/auditx/check.py --repo-root . --profile STRICT`  
  - result: `pass` (`findings=1310`, `promoted_blockers=0`)

- TestX PASS (POLL-2 required suite):  
  `py -3 tools/xstack/testx/runner.py --repo-root . --profile STRICT --subset test_exposure_accumulation_deterministic,test_threshold_crossing_event,test_measurement_artifact_created,test_compliance_report_deterministic,test_replay_window_hash_match`  
  - result: `pass` (`selected_tests=7`; `test_replay_window_hash_match` expands to existing cross-domain tests sharing the same ID)

- stress harness PASS (POLL-2 replay window):  
  `py -3 tools/pollution/tool_replay_exposure_window.py --state-path build/pollution/pollution_exposure_replay_state.json --expected-state-path build/pollution/pollution_exposure_replay_state.json`  
  - result: `complete`  
  - deterministic_fingerprint: `aab6e7d74d7e1d96d30bf60debf197db3ec99dff7960c042702718c6be2004c0`

- strict build gate:  
  `py -3 tools/xstack/run.py strict --repo-root . --cache on`  
  - result: `refusal` due pre-existing global strict-lane blockers outside POLL-2 scope (`compatx`, `registry_compile`, `session_boot`, global strict `testx`, `packaging.verify`).

## 7) Contract Impact and Readiness

Contracts/schemas changed in POLL-2:

- Added POLL exposure/compliance schema family:
  - `schema/pollution/exposure_threshold.schema`
  - `schema/pollution/health_risk_event.schema`
  - `schema/pollution/pollution_measurement.schema`
  - `schema/pollution/compliance_report.schema`
- Added registries:
  - `data/registries/exposure_threshold_registry.json`
  - `data/registries/pollution_sensor_type_registry.json`
- Added process/task declarations for measurement/compliance flows.

Determinism/replay impact:

- deterministic ordering preserved for subjects, pollutants, and region processing.
- no wall-clock sources introduced.
- replay hash verification tool confirms stable POLL-2 hash-chain evolution.

Ready for POLL-3 stress/regression envelope and LOGIC-0 integration:

- exposure/measurement/compliance flows are process-bound, explainable, and replay-verifiable.
- enforcement rails exist for process-only exposure mutation and anti-omniscient pollution UI discipline.
