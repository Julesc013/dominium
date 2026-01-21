# Execution Model (CANON0)

Status: binding.
Scope: Work IR, Access IR, deterministic scheduling, budgets, and HWCAPS0.

This is the human-readable summary of the execution substrate and performance
model. It does not replace the schema specifications.

## Invariants
- Authoritative work must be expressed as Work IR + Access IR.
- Scheduling and commits are deterministic.
- Budgets degrade deterministically; no silent fallback.

## Work IR and Access IR
Authoritative work is emitted as Work IR:
- TaskGraph and TaskNode records describe what should execute.
- Each TaskNode declares determinism_class, AccessSet, CostModel, and law_targets.
- Access IR declares reads, writes, and reductions with deterministic operators.

Game systems emit Work IR; execution backends consume it. No authoritative work
may bypass this path.

## Deterministic scheduling and commit
Schedulers may choose execution order, but only within deterministic rules:
- Ordering keys are stable (phase_id, task_id, sub_index).
- Reductions use fixed-tree deterministic algorithms.
- Authoritative commits are applied in stable order, regardless of parallelism.

## Parallelism as backend swap
Parallel execution is a backend choice, not a gameplay decision. Different
backends must produce identical authoritative results. Derived tasks may run
speculatively; authoritative tasks may not.

## Budgets and degradation
Every task declares a cost model. Budget profiles decide how much work can run:
- Under budget: execute normally.
- Over budget: defer, degrade fidelity, or refuse explicitly.

Silent fallback is forbidden; degradations are audited.

## Hardware capability abstraction (HWCAPS0)
SysCaps describe conservative hardware signals. Execution policy uses SysCaps
and law outputs to select backends deterministically. Unknown caps are treated
as unavailable. GPU usage is derived-only.

## Forbidden assumptions
- Authoritative work may bypass Work IR.
- Backend choice can change simulation outcomes.
- Unknown hardware capabilities are treated as available.

## Dependencies
- Execution schema: `schema/execution/README.md`
- SysCaps policy: `docs/arch/SYS_CAPS_AND_EXEC_POLICY.md`

## See also
- `schema/execution/README.md`
- `docs/arch/EXECUTION_SUBSTRATE_AUDIT.md`
- `docs/arch/EXECUTION_REORDERING_POLICY.md`
- `docs/arch/DETERMINISTIC_REDUCTION_RULES.md`
- `docs/arch/SYS_CAPS_AND_EXEC_POLICY.md`
