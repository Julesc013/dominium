Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Reference Interpreter Baseline

Status: BASELINE (META-REF-0)  
Last Reviewed: 2026-03-07  
Version: 1.0.0  
Scope: deterministic runtime-vs-reference equivalence checks for critical subsystems under STRICT/FULL validation profiles.

## 1) Implemented Evaluators

Active reference evaluators (registry: `data/registries/reference_evaluator_registry.json`):

- `ref.energy_ledger`
  - subsystem: `phys.energy_ledger`
  - equivalence kind: `tolerance_bounded`
- `ref.coupling_scheduler`
  - subsystem: `meta.coupling_scheduler`
  - equivalence kind: `exact`
- `ref.system_invariant_check`
  - subsystem: `sys.boundary_invariant_check`
  - equivalence kind: `exact`
- `ref.compiled_model_verify`
  - subsystem: `meta.compiled_model_verify`
  - equivalence kind: `exact`

Prepared stubs (explicitly non-active):

- `ref.proc_quality_baseline` (next series: `PROC-2`)
- `ref.logic_eval_engine` (next series: `LOGIC-4`)

Runtime surfaces:

- evaluator engine: `src/meta/reference/reference_engine.py`
- harness tool: `tools/meta/tool_run_reference_suite.py`

## 2) FULL Profile Curated Seed Set

Curated seed/window set for reference suite execution:

- `seed=1107`, `tick_range=[0,3]`
- `seed=1731`, `tick_range=[0,3]`
- `seed=1732`, `tick_range=[0,3]`
- `seed=1733`, `tick_range=[0,3]`
- `seed=1734`, `tick_range=[0,3]`
- `seed=1735`, `tick_range=[0,3]`

Observed harness runs:

- `python tools/meta/tool_run_reference_suite.py --seed 1107 --tick-start 0 --tick-end 3 --out-path .xstack_cache/meta_ref0/reference_suite_seed1107.json`
  - result: `complete`
  - mismatches: `0`
- `python tools/meta/tool_run_reference_suite.py --seed 1731 --tick-start 0 --tick-end 3 --out-path .xstack_cache/meta_ref0/reference_suite_seed1731.json`
  - result: `complete`
  - mismatches: `0`

## 3) Discrepancy Report Format

On mismatch, harness emits:

- path: `docs/audit/REFERENCE_MISMATCH_<seed>.md`
- includes:
  - `seed`
  - `tick_range`
  - mismatch count
  - evaluator rows with:
    - `evaluator_id`
    - `run_id`
    - `discrepancy_summary`

Derived run records are normalized and fingerprinted via `reference_run_record` rows with:

- `run_id`
- `evaluator_id`
- `seed`
- `tick_range`
- `runtime_output_hash`
- `reference_output_hash`
- `match`
- optional discrepancy summary

## 4) Gate Snapshot

- RepoX STRICT: `refusal` (`findings=36`)  
  command: `python tools/xstack/repox/check.py --profile STRICT`  
  note: repository-global pre-existing blockers remain; no `INV-CRITICAL-SUBSYSTEM-REF-AVAILABLE` findings were reported.

- AuditX STRICT: `pass` (`findings=2212`, promoted blockers not raised)  
  command: `python tools/xstack/auditx/check.py --profile STRICT`

- TestX (META-REF-0 subset): `pass` (`selected_tests=5`)  
  command:  
  `python tools/xstack/testx/runner.py --profile FAST --subset test_reference_suite_deterministic,test_energy_ledger_ref_matches_runtime,test_coupling_scheduler_ref_matches_runtime,test_invariant_ref_matches_runtime,test_compile_verify_ref_matches_runtime`

- FULL-profile reference suite (curated seeds): `pass` for executed seeds  
  command: `python tools/meta/tool_run_reference_suite.py ...`

- strict build (`tools/xstack/run.py strict`): timed out in this run window, no completion status captured.

## 5) Readiness

- Critical evaluator coverage for META-REF-0 initial scope (PHYS/COUPLE/SYS/COMPILE): complete.
- Enforcement hooks are wired:
  - RepoX invariant: `INV-CRITICAL-SUBSYSTEM-REF-AVAILABLE`
  - AuditX analyzer: `E301_MISSING_REFERENCE_EVALUATOR_SMELL`
- Deterministic discrepancy artifacts and replay-friendly output hashes are in place.
- Ready for `META-INSTR-0` and LOGIC-series reference expansion.
