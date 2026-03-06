# Yield & Defect Baseline

Status: BASELINE
Last Updated: 2026-03-06
Scope: PROC-2 yield/defect models, deterministic quality outcomes, named-RNG policy, and traceability.

## 1) Quality Model Definitions

PROC-2 introduces first-class quality model artifacts and runtime integration:

- `schema/process/yield_model.schema`
- `schema/process/defect_model.schema`
- `schema/process/process_quality_record.schema` (canonical RECORD)
- `schema/materials/batch_quality.schema` updated for run-link traceability fields

Registries:

- `data/registries/yield_model_registry.json`
- `data/registries/defect_model_registry.json`
- `data/registries/defect_flag_registry.json`

Constitutive model types and bindings:

- `model_type.proc_yield_factor_model`
- `model_type.proc_defect_model`
- `model.proc_yield_factor.default`
- `model.proc_defect.default`

## 2) Deterministic vs Named RNG Policy

Default behavior is deterministic:

- yield factor and quality grade derive from deterministic model inputs
- defect flags and severity derive from deterministic model inputs

Optional stochastic behavior is policy-gated:

- enabled only when model/registry allows stochastic path
- named RNG stream usage is seeded deterministically from run-context fields
- RNG usage is emitted in run-state quality RNG events for proof/replay visibility

Enforcement added:

- `INV-YIELD-DEFECT-MODEL-DECLARED`
- `INV-NO-ADHOC-YIELD`
- `INV-NO-UNDECLARED-RNG`
- AuditX analyzers:
  - `E283_INLINE_YIELD_SMELL`
  - `E284_DEFECT_FLAG_BYPASS_SMELL`

## 3) Traceability Guarantees

At run end (`src/process/process_run_engine.py`):

- quality models are evaluated via META-MODEL engine
- canonical `process_quality_record` is emitted
- output `batch_quality` rows include traceability links to:
  - process_id/version
  - run_id
  - input batch IDs
  - tool IDs
  - environment snapshot hash
- deterministic quality hash chains are produced:
  - `process_quality_hash_chain`
  - `batch_quality_hash_chain`

Replay tool:

- `tools/process/tool_replay_quality_window.py`

## 4) Validation Summary

Relevant invariants/docs upheld:

- Canon: `docs/canon/constitution_v1.md`
- Glossary: `docs/canon/glossary_v1.md`
- A1 determinism, A2 process-only mutation, provenance/replay discipline
- PROC-2 invariants listed above

Contract/schema impact:

- Changed: process quality schema surface, model registries/model types, process run finalization semantics for quality outputs
- Unchanged: process capsule behavior (PROC-5), QC sampling workflow (PROC-3), domain semantics

Commands executed:

- RepoX STRICT:
  - `python tools/xstack/repox/check.py --repo-root . --profile STRICT`
  - Status: `refusal` (repository-wide pre-existing blockers outside PROC-2 scope; PROC-2 undeclared schema/registry topology blockers resolved after topology regeneration).
- AuditX STRICT:
  - `python tools/xstack/auditx/check.py --repo-root . --profile STRICT`
  - Status: `fail` (pre-existing promoted blocker `E240_UNCLASSIFIED_ARTIFACT_SMELL`).
- TestX (PROC-2 subset):
  - `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_yield_deterministic_default,test_defects_deterministic_default,test_named_rng_quality_logged,test_batch_quality_traceability_links,test_replay_quality_hash_match`
  - Status: `pass` (`selected_tests=5`).
- Stress harness (many runs):
  - Deterministic 256-run quality sweep executed via PROC-2 fixtures.
  - Artifact: `build/process/proc2_stress_report.json`
  - Status: `complete`
  - `first_run_suite_fingerprint`: `9af8013356a21d32e6005b443d8c575bcfb89e5ab859e1e5e6d7d9a6ab42b6c9`
- Replay window verification:
  - `python tools/process/tool_replay_quality_window.py --state-path build/process/proc2_report.json`
  - Status: `complete`
  - `process_quality_hash_chain`: `faa818828ba58d33955cba5aeaa2fbf2fc74312dc9d15b923863249d52a70fee`
  - `batch_quality_hash_chain`: `a3015deda9478d1a722fbf4973ca7b9d75d08f42fb72d507f7f6fa6488229487`
- Strict build:
  - `python tools/xstack/run.py strict --repo-root . --cache on`
  - Status: timed out in this execution window (`~904s`), no successful completion artifact produced.

## 5) Topology Map

Topology map regenerated:

- `docs/audit/TOPOLOGY_MAP.json`
- `docs/audit/TOPOLOGY_MAP.md`
- fingerprint: `5b74aa80d97338243b05555405eb3ddc20a34de6fb0e21ccb25fb2677b81dc35`

## 6) Readiness for PROC-3 (QC Sampling)

- [x] Yield and defect models are first-class and registry-driven
- [x] Deterministic defaults enforced; named RNG path explicit and logged
- [x] Canonical process quality records emitted and hash-chained
- [x] Output batch quality carries run/input/tool/environment traceability links
- [x] Replay tool verifies deterministic quality hash chains
- [ ] Repository-wide strict gates fully green (blocked by existing global findings outside PROC-2 scope)
