# EXEC-AUDIT0 Execution Substrate Audit

Status: binding, non-negotiable.
Scope: enforcement of Work IR, Access IR, and law admission across all systems.

## Purpose
EXEC-AUDIT0 seals the execution substrate by removing bypass paths and
requiring every sim-affecting unit of work to flow through Work IR with
declared access and law admission.

This is not a feature change. It is a contract audit.

## What Is Enforced

1) Work IR completeness
   - TaskNodes must set determinism_class, AccessSet, CostModel, phase_id,
     and commit_key.
   - AUTHORITATIVE tasks must declare non-empty law_targets.

2) Access IR integrity
   - AccessSets must be declared and non-empty.
   - Conflicts are detected deterministically.

3) Law admission
   - Scheduling must invoke law evaluation before execution.
   - Refusals prevent execution; transforms re-evaluate deterministically.

4) Bypass elimination
   - Game code must not include scheduler backends.
   - Game code must not include engine/modules headers.
   - Game code must not spawn threads.

## Enforcement Points

CI gates and tests map to the following IDs:
- EXEC-AUDIT0-BYPASS-001
- EXEC-AUDIT0-IR-REQ-002
- EXEC-AUDIT0-LAW-REQ-003
- EXEC-AUDIT0-ACCESS-REQ-004

Scheduler equivalence is verified by the `execution_equivalence` test
(EXEC2 vs EXEC3 behavior).

See `docs/ci/CI_ENFORCEMENT_MATRIX.md` for the complete matrix.

## Fixing Common Violations

- Missing AccessSet: add AccessSet emission in system task generation.
- Missing CostModel: assign a bounded cost estimate per task.
- Missing law_targets: use schema-defined targets; do not hard-code ad hoc tags.
- Direct scheduler usage: replace with system registry emission.
- Thread creation in game: move concurrency to engine backends.

## Future Systems

All new systems must:
- Emit Work IR only (no direct execution).
- Declare AccessSets for every task.
- Declare law_targets for authoritative tasks.
- Remain deterministic under batch vs step equivalence.

## See also
- `docs/architecture/EXECUTION_MODEL.md`
- `schema/execution/README.md`
