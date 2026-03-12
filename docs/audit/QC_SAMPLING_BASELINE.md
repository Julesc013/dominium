Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# QC Sampling Baseline

Status: BASELINE
Last Updated: 2026-03-06
Scope: PROC-3 deterministic QC sampling, measurement artifacts, inspection outcomes, and replay/proof hooks.

## 1) Sampling Strategies

PROC-3 introduces policy-driven QC sampling with deterministic selection:

- `sample.hash_based`
- `sample.every_n`
- `sample.risk_weighted`

Policy and procedure artifacts:

- `schema/process/qc_policy.schema`
- `schema/process/qc_result_record.schema` (canonical RECORD)
- `schema/process/test_procedure.schema`
- `data/registries/qc_policy_registry.json`
- `data/registries/sampling_strategy_registry.json`
- `data/registries/test_procedure_registry.json`

Runtime integration:

- `src/process/qc/qc_engine.py`
- `src/process/process_run_engine.py`

## 2) Integration Points

QC run-end behavior now includes:

- deterministic sampling decision and `qc_sampling_decision_rows`
- test-procedure measurement observations
- canonical QC result rows (`pass/fail/rework/reject/accept_warning`)
- deterministic follow-up actions (rework requests, warnings, reject flags)
- stabilization/certification hooks for downstream PROC/SYS enforcement

Epistemics and explain hooks:

- inspection section: `section.process.qc_summary`
- explain contracts:
  - `explain.qc_failure`
  - `explain.qc_sampling_decision`

## 3) Deterministic Guarantees

Determinism constraints upheld:

- no wall-clock use in QC sampling decisions
- stable ordering by `batch_id` and `test_id`
- deterministic hash chains:
  - `qc_result_hash_chain`
  - `sampling_decision_hash_chain`
- replay verifier:
  - `tools/process/tool_replay_qc_window.py`

Proof-bundle extensions wired:

- `src/control/proof/control_proof_bundle.py`
  - `qc_result_hash_chain`
  - `sampling_decision_hash_chain`

## 4) Validation Summary

Relevant invariants/docs upheld:

- Canon: `docs/canon/constitution_v1.md` (A1 determinism, A2 process-only mutation, A6 provenance)
- Glossary: `docs/canon/glossary_v1.md`
- PROC-3 enforcement invariants:
  - `INV-QC-POLICY-DECLARED`
  - `INV-SAMPLING-DETERMINISTIC`
  - `INV-NO-ADHOC-INSPECTION`

Contract/schema impact:

- Changed: PROC QC policy/test schema surface, QC registries, process run QC decision/output semantics, proof-bundle hash surface.
- Unchanged: process capsule behavior (PROC-5), yield/defect model semantics (PROC-2), core domain laws.

Validation level:

- FAST minimum met with explicit PROC-3 TestX subset.

Commands executed:

- RepoX STRICT:
  - `python tools/xstack/repox/check.py --repo-root . --profile STRICT`
  - Status: `refusal` (repository-wide pre-existing blockers outside PROC-3 scope remain).
- AuditX STRICT:
  - `python tools/xstack/auditx/check.py --repo-root . --profile STRICT`
  - Status: `fail` (promoted blocker remains: `E240_UNCLASSIFIED_ARTIFACT_SMELL`, outside PROC-3 scope).
- TestX (PROC-3 subset):
  - `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_hash_sampling_deterministic,test_every_n_sampling_deterministic,test_qc_fail_triggers_action,test_qc_results_traceable,test_replay_qc_hash_match`
  - Status: `pass` (`selected_tests=5`).
- Stress harness (many batches):
  - Deterministic 256-run QC sweep using PROC-3 fixtures.
  - Artifact: `build/process/proc3_stress_report.json`
  - Status: `complete`
  - `first_run_suite_fingerprint`: `2fc62d47acb223d02be5125a0a3e1c68f6e5906ebafb662821ade8ec2a005c47`
  - `deterministic_match`: `true`
- Replay window verification:
  - `python tools/process/tool_replay_qc_window.py --state-path build/process/proc3_report.json`
  - Status: `complete`
  - `qc_result_hash_chain`: `795451e667168e1efcfa7ab20377caa08188cb95197ef23f77ac33c0447e4cff`
  - `sampling_decision_hash_chain`: `56b3ad05b4dfff89ccfefbd0fea21ae02744ecd050e4f6be901691e1fa4eae78`
- Strict build:
  - `python tools/xstack/run.py strict --repo-root . --cache on`
  - Status: timed out in this execution window (`~904s`), no successful completion artifact produced.

## 5) Topology Map

Topology map regenerated:

- `docs/audit/TOPOLOGY_MAP.json`
- `docs/audit/TOPOLOGY_MAP.md`
- fingerprint: `ec0fdc75aeb508b594e2e67abfb496ee6191e112ce7aa4fee535cba4afb5b53b`

## 6) Readiness for PROC-4 (Stabilization Scoring)

- [x] Deterministic sampling strategies implemented and replay-verifiable
- [x] QC result records are canonical and traceable
- [x] Measurement observations integrated into QC flow
- [x] Rework/reject/accept-warning policy actions integrated
- [x] Hooks emitted for stabilization/certification pathways
- [ ] Repository-wide strict gates fully green (blocked by existing global findings outside PROC-3 scope)
