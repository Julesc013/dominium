Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Execution Reordering Policy (EXEC0b)

Status: binding.
Scope: legal task reordering, parallelism, and commit ordering.
Authority: ARCH0, then EXEC0. This policy is subordinate to ARCH0.

## Purpose
Define deterministic rules for reordering, parallel execution, and commit
ordering so schedulers, kernels, and distributed backends cannot break
authoritative determinism.

## Canonical Execution Model
1. TaskGraph emission produces a stable set of TaskNodes.
2. Scheduler chooses an execution order subject to this policy.
3. For each phase:
   - tasks may run in parallel only if allowed by determinism class and
     AccessSet conflict rules
   - authoritative commits occur only at deterministic commit points
4. Any reordering must preserve deterministic equivalence classes.
5. Any reduction must be performed by a deterministic algorithm.

## Stable Ordering Keys
When an ordering is required, the canonical ordering key is:
- (phase_id, task_id, sub_index)

Where:
- phase_id is the current phase barrier identifier,
- task_id is the TaskNode stable identifier,
- sub_index is a deterministic sub-order for internal outputs.

## Reordering Rules by Determinism Class

### STRICT
- No reordering beyond proven non-interaction.
- Writes must be exclusive.
- If multiple tasks are eligible, commit order MUST follow task_id ordering.

### ORDERED
- Reordering is allowed only under a deterministic total order:
  - stable topological order, tie-break by (phase_id, task_id).
- Parallel execution is allowed only if commit order is deterministic and
  identical to the canonical order.

### COMMUTATIVE
- Reordering is allowed only if:
  - AccessSet declares commutative reductions, and
  - reductions use fixed-tree deterministic reduction, and
  - no conflicting writes exist.
- Parallelism MUST converge identically to the canonical reduction result.

### DERIVED
- May be reordered freely, but:
  - must not affect authoritative state or hashes,
  - outputs must be tagged non-authoritative,
  - results must be discardable.

## AccessSet-Based Conflict Rules
Conflict detection uses AccessSet declarations:
- Read/Read: non-conflicting.
- Read/Write: conflicting unless same range proven independent.
- Write/Write: conflicting unless ranges are disjoint and declared.
- Reduce/Reduce: allowed only if same deterministic operator and fixed-tree
  reduction is used.
- Write/Reduce: conflicting unless explicitly allowed by operator semantics
  (rare and must be documented).

Ranges must be declared as:
- component ranges
- chunk/tile ranges
- stable ID sets

No pointer-chasing or implicit access is allowed.

## Commit Order Rules
Authoritative writes must be committed only at deterministic commit points.
Commit order MUST be stable and reproducible:
- commit ordering key = (phase_id, task_id, sub_index)

Parallel execution may compute results concurrently, but commits must be applied
in the same stable order every run.

## Phase Barriers and Write Domains
Each phase declares an explicit write domain (which components may be written).
Within a phase:
- shared mutation is forbidden unless reduction rules apply.
Between phases:
- data becomes stable for subsequent phases.

## Speculation Policy (Derived Only)
Speculative execution is allowed ONLY for DERIVED tasks:
- speculation writes to shadow buffers,
- results are discardable,
- no authoritative commits,
- budgets are strictly enforced.

Speculative authoritative work is forbidden.

## Distributed Placement (Preview Constraints)
- Only shard-owned tasks may execute on a shard.
- Cross-shard dependencies become messages with arrival_tick ordering.
- No synchronous cross-shard reads.
- Deterministic ordering is preserved at shard boundaries.

## Forbidden Patterns
- Execution policy encoded in gameplay code.
- Hidden global scans or implicit iteration.
- Nondeterministic scheduling tricks ("first ready wins", work stealing order).
- Reordering that changes the canonical commit order.