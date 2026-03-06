# Process Capsule Baseline

Status: BASELINE
Last Updated: 2026-03-06
Scope: PROC-5 ProcessCapsule generation/execution, compiled-model runtime path, invalidation hooks, proof/replay, enforcement, and TestX closure.

## 1) Capsule Generation and Execution Semantics

PROC-5 capsule generation and macro execution are implemented with deterministic process-only mutation paths:

- Generation engine:
  - `src/process/capsules/capsule_builder.py`
  - process: `process.process_capsule_generate`
- Execution engine:
  - `src/process/capsules/capsule_executor.py`
  - process: `process.process_capsule_execute`
- Runtime wiring:
  - `tools/xstack/sessionx/process_runtime.py`

Generation guarantees:

- requires `maturity_state == capsule_eligible`
- requires registered tolerance/error-bound policy
- requires declared state vector owner/definition
- emits canonical capsule generation record rows and decision metadata

Execution guarantees:

- validates validity domain before macro execution
- emits canonical run + capsule execution records for successful runs
- emits deterministic forced-expand records on invalid/out-of-domain execution
- routes quality/QC through declared PROC-2/PROC-3 pathways
- records energy/emission outputs and provenance links

## 2) Compiled Model Integration

COMPILE-0 integration is active for capsules when compiled model metadata is present and valid:

- compile hooks are consumed during capsule generation
- compiled model validity requires:
  - compiled model row presence
  - equivalence proof reference
  - validity domain reference
  - compiled-model state vector definition availability
- runtime executes compiled model path when valid and falls back to uncompiled capsule behavior otherwise

Critical state-vector wiring fixed in this phase:

- compiled model state vector definition/snapshot rows are now propagated from generation into runtime/execution inputs
- this unblocks deterministic `compiled_model_used=true` executions under valid inputs

## 3) Invalidation Rules

Process capsule invalidation hooks are integrated and deterministic:

- QC failure spike threshold
- drift score threshold
- spec revision mismatch
- out-of-domain input features (forced expand)

Invalidation outcomes:

- canonical invalidation record row
- forced expand event row (when allowed)
- refusal path when forced expand is denied by policy

## 4) Proof / Replay / Topology

Proof surfaces used for PROC-5 replay and reporting:

- `process_capsule_generation_hash_chain`
- `process_capsule_execution_hash_chain`
- `compiled_model_hash_chain`

Replay tool:

- `tools/process/tool_replay_capsule_window.py`

Replay verification run:

- command: `python tools/process/tool_replay_capsule_window.py --state-path build/process/proc5_report.json`
- status: `complete`
- observed hashes:
  - capsule_generation_hash_chain: `c82174b0df1f503fed164413d25c254965292137ed1012b9d312b395e7bfd0c3`
  - capsule_execution_hash_chain: `574ae6a74a0546c379ac84ae4ea6d0e8b54ccd75df2a50dab28e7dcfa32f4b8b`
  - compiled_model_hash_chain: `a4de245d7eb0489936916c2e5b98f88d1f4dde45a5ade3432df32f08da128a98`

Topology map refresh:

- command: `python tools/governance/tool_topology_generate.py --repo-root . --out-json docs/audit/TOPOLOGY_MAP.json --out-md docs/audit/TOPOLOGY_MAP.md`
- status: `complete`
- topology fingerprint: `d8e848dfc9a0250cded407428525d645f9d0e1a4b0254ab85c94525662c727a0`

## 5) TestX Coverage (PROC-5)

Required PROC-5 tests are present and passing (FAST subset):

- `test_capsule_generate_requires_eligible`
- `test_capsule_execution_deterministic` (existing SYS-2 + PROC-5 coverage)
- `test_capsule_out_of_domain_forces_expand`
- `test_compiled_model_used_when_valid`
- `test_replay_capsule_hash_match`

Command:

- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_capsule_generate_requires_eligible,test_capsule_execution_deterministic,test_capsule_out_of_domain_forces_expand,test_compiled_model_used_when_valid,test_replay_capsule_hash_match`
- status: `pass` (`selected_tests=6` due shared test id usage)

## 6) Stress Harness Summary (Many Capsule Executions)

Deterministic stress sweep executed for mixed capsule workloads (compiled + forced-expand cases):

- artifact: `build/process/proc5_stress_report.json`
- scenario: `proc5_capsule_stress_mixed_96`
- status: `complete`
- executions: `96`
- complete executions: `87`
- forced expands: `9`
- compiled-model-used executions: `29`
- suite fingerprint: `ea575f0fa3c4c956c660de49379070a8daf092374315707f3f3505524ce4a3fc`
- deterministic match: `true`

## 7) Validation Summary and Gate Status

Relevant invariants/docs upheld:

- Canon: `docs/canon/constitution_v1.md`
- Glossary: `docs/canon/glossary_v1.md`
- PROC-5 invariants:
  - `INV-CAPSULE-ELIGIBLE-REQUIRED`
  - `INV-CAPSULE-STATEVEC-REQUIRED`
  - `INV-CAPSULE-ERROR-BOUNDS-REQUIRED`
  - `INV-CAPSULE-EXECUTION-RECORDED`

Contract/schema impact statement:

- Changed in this completion pass: runtime/analyzer/test/report wiring for PROC-5 behavior and enforcement fit.
- Unchanged in this completion pass: schema IDs/versions, domain semantics, wall-clock policy, determinism policy.

Gates:

- RepoX STRICT:
  - command: `python tools/xstack/repox/check.py --repo-root . --profile STRICT`
  - status: `refusal` (`findings=27`, `refusals=10`)
  - blockers are pre-existing/global outside PROC-5 scope (RWAM series declarations, E240 provenance classification gap, existing SYS envelope refusals, worktree hygiene).
- AuditX STRICT:
  - command: `python tools/xstack/auditx/check.py --repo-root . --profile STRICT`
  - status: `fail` (`promoted_blockers=1`)
  - remaining blocker: `E240_UNCLASSIFIED_ARTIFACT_SMELL` at `data/registries/provenance_classification_registry.json` (pre-existing/global).
- TestX:
  - status: `pass` for required PROC-5 subset.
- Stress harness:
  - status: `pass` (deterministic match true).
- Strict build:
  - command: `python tools/xstack/run.py strict --repo-root . --cache on`
  - status: `refusal` (global strict pipeline blockers: compatx/refusal, repox/auditx/testx ecosystem findings outside PROC-5 scope).

## 8) Readiness for PROC-6 (Drift Detection)

- [x] Capsule generation is maturity-gated and state-vector declared
- [x] Capsule execution is deterministic and recorded
- [x] Compiled-model execution path is validatable and used when valid
- [x] Forced-expand/out-of-domain behavior is deterministic and replay-verifiable
- [x] Invalidation hooks for QC/drift/spec-change are integrated
- [ ] Repository-wide STRICT gates are globally green (blocked by pre-existing non-PROC-5 findings)
