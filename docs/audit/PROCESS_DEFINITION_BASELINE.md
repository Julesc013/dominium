# Process Definition Baseline

Status: BASELINE
Last Updated: 2026-03-06
Scope: PROC-1 ProcessDefinition schemas, deterministic validator, and canonical run engine.

## 1) Schema Summary

PROC-1 introduces versioned process artifacts under `schema/process/`:

- `process_definition.schema` (versioned step-graph definition)
- `process_step.schema` (typed step contracts)
- `process_run_record.schema` (canonical RECORD)
- `process_step_record.schema` (canonical RECORD)

CompatX integration now tracks these schema keys in `tools/xstack/compatx/version_registry.json`:

- `process_definition`
- `process_step`
- `process_run_record`
- `process_step_record`

Registry addition:

- `data/registries/process_registry.json` with deterministic PROC archetype IDs.

## 2) Run Lifecycle

Runtime path implemented in `src/process/process_run_engine.py`:

- `process_run_start` validates ProcessDefinition and emits canonical running record.
- `process_run_tick` executes deterministic eligible steps by stable toposort + cost budget.
- `process_run_end` finalizes canonical record, output refs, and provenance fingerprint.

Step semantics implemented for:

- `action` (task request + completion signal)
- `transform` (domain process output + ledger/entropy enforcement)
- `measure` (derived observation artifact recording)
- `verify` (report artifact + pass/fail status)
- `wait` (temporal readiness gating)

Deterministic refusal codes:

- `refusal.process.invalid_definition`
- `refusal.process.run_not_found`
- `refusal.process.ledger_required`
- `refusal.process.direct_mass_energy_mutation`

## 3) Determinism Properties

Validator guarantees (`src/process/process_definition_validator.py`):

- DAG-only step graph enforcement.
- Stable topological order by `step_id` tie-break.
- Action-template/temporal-domain bindings validated against registries.
- Measure/verify steps must map to META-INFO outputs.

Run engine guarantees:

- deterministic step eligibility and ordering
- deterministic budget degradation logs (`deferred_non_critical_budget`)
- canonical deterministic fingerprints for run/step records
- no wall-clock dependence

Proof/compaction integration:

- Canonical: process run + step records.
- Derived compactable: process measurement artifacts.
- Replay tool: `tools/process/tool_replay_process_window.py`.

## 4) Validation Summary

Relevant invariants/docs upheld in this pass:

- Canon: `docs/canon/constitution_v1.md`
- Glossary: `docs/canon/glossary_v1.md`
- Process-only mutation (A2), determinism (A1), provenance (A6)
- RepoX PROC invariants:
  - `INV-PROCESS-STEPS-MAP-TO-ACTION-GRAMMAR`
  - `INV-PROCESS-RUN-RECORD-CANONICAL`
  - `INV-NO-IMPLICIT-WORKFLOWS`

Contract/schema impact:

- Changed: PROC schema surface + CompatX registry key set + process archetype registry.
- Unchanged: domain semantics, capsule behavior, yield/defect modeling (deferred to PROC-2+).

Commands executed:

- RepoX STRICT:
  - `python tools/xstack/repox/check.py --repo-root . --profile STRICT`
  - Status: `refusal` (repository-wide blockers, including pre-existing non-PROC findings).
- AuditX STRICT:
  - `python tools/xstack/auditx/check.py --repo-root . --profile STRICT`
  - Status: `fail` (promoted blocker remains: `E240_UNCLASSIFIED_ARTIFACT_SMELL`).
- TestX (PROC-1 subset):
  - `python tools/xstack/testx_all.py --repo-root . --profile FAST --cache on --subset test_process_definition_dag_validation,test_toposort_stable,test_process_run_records_canonical,test_wait_step_temporal_domain_respected,test_replay_process_hash_match`
  - Status: `pass` (`selected_tests=5`).
- Stress harness (many small process runs):
  - Deterministic 256-run smoke executed via process run engine and replay verification.
  - Replay command: `python tools/process/tool_replay_process_window.py --state-path build/process/proc1_report.json`
  - Status: `pass`
  - `process_run_record_hash_chain`: `4776555aea2356fea190ecdc93f92695f70d60c9258b95074b598b8e039c9e59`
  - `process_step_record_hash_chain`: `5fa0236c67cc76c17f2b63a175235edf0187d3ad15b82728ed0e0770793a00e1`
- Strict build:
  - `python tools/xstack/run.py strict --repo-root . --cache on`
  - Status: timed out in this run window (`~904s`), no successful completion artifact produced.

## 5) Topology Map

Topology map regenerated:

- `docs/audit/TOPOLOGY_MAP.json`
- `docs/audit/TOPOLOGY_MAP.md`
- fingerprint: `76ea7ea649b0d1a46538a2c894b040ed8360a8a950c7bc4d11a3f580bb309268`

## 6) Readiness for PROC-2

PROC-2 readiness status:

- [x] ProcessDefinition schema + validator baseline established
- [x] Canonical run/step event sourcing established
- [x] Ledger/entropy enforcement for transform steps integrated
- [x] Replay/proof hooks present for process run windows
- [x] PROC-1 targeted TestX and stress smoke pass
- [ ] Repository-wide strict gates fully green (blocked by existing global findings)
