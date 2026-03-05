# Pollution Dispersion Baseline

Status: BASELINE (POLL-1)  
Date: 2026-03-05  
Scope: POLL-1 deterministic P1 dispersion, decay/deposition transforms, exposure accumulation stub, explain/inspection integration, proof replay hooks, and enforcement.

## 1) Dispersion Rule

Canonical POLL-1 dispersion behavior executes through `process.pollution_dispersion_tick` and process-mediated field mutation (`process.field_update`).

Deterministic update contract:

- concentration field per pollutant: `field.pollution.<type>_concentration`
- fixed-tick local diffusion proxy with deterministic cell/neighbor ordering
- optional wind directional bias from `field.wind` / `field.wind_vector` samples
- no adaptive timestep, no CFD/Navier-Stokes

Primary implementation surfaces:

- `src/pollution/dispersion_engine.py`
- `tools/xstack/sessionx/process_runtime.py`
- `data/registries/pollution_field_policy_registry.json`

## 2) Decay and Deposition Models

Decay/deposition remain explicit constitutive transforms; no silent disappearance:

- decay models from `data/registries/pollution_decay_model_registry.json`
- deposition rows emitted and hash-chained (`pollution_deposition_hash_chain`)
- dispersion rows include per-step decay/deposition terms for explainability

Proof surface integration includes:

- `pollution_field_hash_chain`
- `deposition_hash_chain`

## 3) Exposure Stub

POLL-1 exposure stays deterministic and process-bound:

- exposure state increments from local concentration sampling
- subject ordering: stable by `subject_id`
- pollutant ordering: stable by `pollutant_id`
- hazard hook stub materialized as `hazard.health_risk_stub`

No medical simulation is introduced in POLL-1.

## 4) Governance and Invariants

Constitutional/invariant coverage upheld:

- Canon axioms: determinism, process-only mutation, observer/render separation, explicit degradation/refusal.
- POLL-specific RepoX invariants:
  - `INV-POLLUTION-FIELD-UPDATE-THROUGH-PROCESS`
  - `INV-NO-DIRECT-CONCENTRATION-WRITE`
  - existing POLL-0 invariants remain active (`INV-POLLUTION-EMIT-THROUGH-PROCESS`, `INV-POLLUTANT-TYPE-REGISTERED`).
- Explain contracts added/active:
  - `explain.pollution_dispersion`
  - `explain.pollution_decay`

Contract/schema impact:

- Changed: proof bundle surface now includes pollution field/deposition chains; process registry now explicitly declares `process.field_update` for POLL field-process discipline.
- Unchanged: no POLL semantic broadening beyond P1; no CFD/meteorology solver introduction; no compat-major migration introduced.

## 5) Gate Execution

Validation level executed: STRICT governance checks + POLL targeted strict tests.

- topology map updated:  
  `py -3 tools/governance/tool_topology_generate.py --repo-root . --out-json docs/audit/TOPOLOGY_MAP.json --out-md docs/audit/TOPOLOGY_MAP.md`  
  - result: `complete`  
  - deterministic_fingerprint: `41b8a40363d78b2bce65060f223530712621078693db9404b19a7899557763e1`

- RepoX STRICT:  
  `py -3 tools/xstack/repox/check.py --repo-root . --profile STRICT`  
  - result: `pass` (`findings=17`, warnings only)

- AuditX STRICT:  
  `py -3 tools/xstack/auditx/check.py --repo-root . --profile STRICT`  
  - result: `pass` (`findings=1313`, `promoted_blockers=0`)

- TestX PASS (POLL-1 required suite):  
  `py -3 tools/xstack/testx/runner.py --repo-root . --profile STRICT --subset test_dispersion_deterministic,test_decay_applied,test_deposition_logged,test_exposure_accumulation_deterministic,test_pollution_cross_platform_hash_match`  
  - result: `pass` (`selected_tests=5`)

- stress harness PASS (POLL replay-window verification):  
  `py -3 tools/pollution/tool_replay_dispersion_window.py --state-path build/pollution/pollution_dispersion_replay_state.json --expected-state-path build/pollution/pollution_dispersion_replay_state.json`  
  - result: `complete`

- strict build gate:  
  `py -3 tools/xstack/run.py strict --repo-root . --cache on`  
  - result: `refusal` due pre-existing global baseline blockers outside POLL-1 scope (CompatX/registry compile/session boot/full TestX/packaging strict aggregate failures).

## 6) Readiness

Ready for POLL-2 exposure/health/compliance expansion:

- deterministic concentration fields, decay/deposition accounting, and proof/replay hooks are in place
- deterministic exposure accumulation/hazard stub pathway exists
- explain + inspection surfaces are available for pollution concentration/deposition/exposure summaries
