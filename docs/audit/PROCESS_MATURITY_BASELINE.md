# Process Maturity Baseline

Status: BASELINE
Last Updated: 2026-03-06
Scope: PROC-4 stabilization metrics, maturity scoring/state transitions, process certification hooks, capsule eligibility gating, and replay/proof integration.

## 1) Stabilization Score Formula

PROC-4 scoring is implemented as deterministic weighted composition over bounded metrics:

- `runs_count`
- `yield_variance` (consistency term)
- `qc_pass_rate`
- `defect_rate`
- `env_deviation_score`
- `calibration_deviation_score`

Runtime implementation:

- `src/process/maturity/metrics_engine.py`
- `src/process/maturity/maturity_engine.py`
- `data/registries/stabilization_policy_registry.json`

Effective formula:

- `score = (runs + consistency + qc_pass - defect - environment - calibration) / positive_weights`
- bounded to `[0, 1000]`
- deterministic integer arithmetic only.

## 2) Transition Thresholds

Canonical maturity states:

- `exploration`
- `defined`
- `stabilized`
- `certified`
- `capsule_eligible`

Transitions are policy-driven and deterministic:

- thresholds/weights/min runs/horizon from `stabilization_policy_registry`
- lifecycle constraints from `process_lifecycle_policy_registry`
- transition and denial explain artifacts emitted from `process_run_end`.

Key artifacts and records:

- `schema/process/process_metrics_state.schema`
- `schema/process/process_maturity_record.schema` (canonical RECORD)
- `schema/process/stabilization_policy.schema`
- `process_maturity_record_rows` and deterministic maturity observations.

## 3) Certificate Hooks

Process-level certification hooks integrated in run finalization:

- issue credential rows on `certified`/`capsule_eligible` when policy gates pass
- revoke on maturity drop or QC-failure spike conditions
- deterministic cert hash chain:
  - `process_cert_hash_chain`

Runtime touchpoints:

- `src/process/process_run_engine.py`
- `src/process/maturity/maturity_engine.py`

## 4) Proof/Replay Integration

Proof surface includes:

- `metrics_state_hash_chain`
- `process_maturity_hash_chain`
- `process_cert_hash_chain`

Integrated in:

- `src/control/proof/control_proof_bundle.py`

Replay tool:

- `tools/process/tool_replay_maturity_window.py`
- wrappers:
  - `tools/process/tool_replay_maturity_window`
  - `tools/process/tool_replay_maturity_window.cmd`

## 5) Validation Summary

Relevant invariants/docs upheld:

- Canon: `docs/canon/constitution_v1.md`
- Glossary: `docs/canon/glossary_v1.md`
- PROC-4 enforcement invariants:
  - `INV-CAPSULE-REQUIRES-CAPSULE_ELIGIBLE`
  - `INV-MATURITY-RECORD-CANONICAL`
  - `INV-NO-MAGIC-UNLOCKS`

Contract/schema impact:

- Changed: process maturity schemas, stabilization policy registry surface, process lifecycle compatibility for `capsule_eligible`, process-run maturity/cert gating behavior, proof bundle hash surface, enforcement rules/analyzers.
- Unchanged: domain semantics, wall-clock policy, nondeterminism policy, process optional boot behavior.

Commands executed:

- RepoX STRICT:
  - `python tools/xstack/repox/check.py --repo-root . --profile STRICT`
  - Status: `refusal` (`findings=27`, pre-existing/global blockers remain outside PROC-4 scope).
- AuditX STRICT:
  - `python tools/xstack/auditx/check.py --repo-root . --profile STRICT`
  - Status: `fail` (`promoted_blockers=1`: `E240_UNCLASSIFIED_ARTIFACT_SMELL`, pre-existing/global).
- TestX (PROC-4 subset):
  - `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_metrics_aggregation_deterministic,test_stabilization_score_deterministic,test_maturity_transition_thresholds,test_capsule_eligibility_requires_state,test_replay_maturity_hash_match`
  - Status: `pass` (`selected_tests=5`).
- Stress harness (many processes):
  - deterministic 32-process x 12-run maturity sweep
  - artifact: `build/process/proc4_stress_report.json`
  - Status: `complete`
  - `suite_fingerprint`: `52dd85f28c74a530977d53b4b2e4c2293c6d5d6915f642503c56bfb6866a66da`
  - `deterministic_match`: `true`
- Replay verification:
  - `python tools/process/tool_replay_maturity_window.py --state-path build/process/proc4_report.json`
  - Status: `complete`
  - `metrics_state_hash_chain`: `16d3c12e9e81a8071de078fea5c91e02eb5a53ea13f09959193e4a4f890f17d0`
  - `process_maturity_hash_chain`: `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`
  - `process_cert_hash_chain`: `6a371e2e8004f6d81aad52ce01611d2655759259d73d1e110fdbab6a4cdcafbd`
- Strict build:
  - `python tools/xstack/run.py strict --repo-root . --cache on`
  - Status: timed out in this execution window (`~904s`), no successful completion artifact produced.

## 6) Topology Map

Topology map regenerated:

- `docs/audit/TOPOLOGY_MAP.json`
- `docs/audit/TOPOLOGY_MAP.md`
- fingerprint: `5001e55c407695e04f85eca407ee27e8281a17125a265686dda909aef62cea24`

## 7) Readiness for PROC-5 (ProcessCapsules)

- [x] Deterministic metrics aggregation implemented and hash-chained
- [x] Deterministic stabilization scoring and threshold transitions implemented
- [x] Process certification issuance/revocation hooks integrated
- [x] Capsule eligibility gating enforced by maturity state and policy
- [x] Explain/inspection contracts added for maturity and denials
- [x] Replay tool validates maturity/cert hash surfaces
- [ ] Repository-wide strict gates fully green (blocked by existing global findings outside PROC-4 scope)
