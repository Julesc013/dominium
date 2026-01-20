# Execution Enforcement Checks (EXEC-AUDIT0)

This document maps execution-substrate rules to their enforcement scripts and tests.

## Rule Mapping

### EXEC-AUDIT0-BYPASS-001
- Mechanism: `scripts/ci/check_execution_contracts.py`
- Failure output: `EXEC-AUDIT0-BYPASS-001: game includes engine/modules or scheduler backend`
- Fix: remove forbidden includes and thread creation calls in `game/`.
 - Scope includes IR-only systems calling legacy execution paths.

### EXEC-AUDIT0-IR-REQ-002
- Mechanism: CTest `execution_contract`, CTest `dominium_work_ir_completeness`
- Failure output: `FAIL: missing access_set_id` or `FAIL: commit_key task mismatch`
- Fix: populate TaskNode fields at emission time.

### EXEC-AUDIT0-LAW-REQ-003
- Mechanism: CTest `execution_contract`
- Failure output: `FAIL: law admission calls mismatch`
- Fix: ensure scheduler calls law evaluation before task execution.

### EXEC-AUDIT0-ACCESS-REQ-004
- Mechanism: CTest `execution_contract`, CTest `dominium_work_ir_completeness`
- Failure output: `FAIL: empty access set` or `FAIL: access conflict not detected`
- Fix: declare AccessSets for all tasks and resolve conflicts deterministically.

## Notes

- These checks are refusal-first and merge-blocking.
- When adding a new system, update the Work IR emission tests before shipping.
- Scheduler equivalence is validated by CTest `execution_equivalence`.
