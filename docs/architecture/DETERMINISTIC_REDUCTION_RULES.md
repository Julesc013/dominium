# Deterministic Reduction Rules (EXEC0b)

Status: binding.
Scope: deterministic reductions for AccessSet reduces.
Authority: ARCH0, then EXEC0. This policy is subordinate to ARCH0.

## Purpose
Define legal, deterministic reduction operators and ordering so parallel and
distributed execution preserves authoritative determinism.

## Allowed Deterministic Reduction Operators
Operators must be deterministic, explicit, and declared in AccessSet:
- integer sum
- integer min/max
- fixed-point sum with explicit rounding rule
- bitwise OR/AND/XOR
- deterministic histogram merge (fixed bin set)
- deterministic set union with stable ordering

## Forbidden in Authoritative Tasks
- floating-point sum/min/max
- "first writer wins" or last-writer semantics
- unordered set merges without normalization
- reductions that depend on thread or work-stealing order

## Fixed-Tree Reduction Requirement
All reductions MUST use fixed-tree deterministic reduction:
- Inputs are ordered by the canonical ordering key
  (phase_id, task_id, sub_index).
- Reduction combines inputs in a fixed binary tree.
- No dynamic or runtime-dependent tree shape is allowed.

## Operator Requirements
Every reduction operator MUST:
- be deterministic for identical inputs,
- be fully specified (including rounding and overflow behavior),
- be valid across target platforms,
- be declared via AccessSet reduce entries.

## Range Requirements
Reduction ranges must be:
- bounded,
- deterministic,
- auditable via AccessSet RangeRef declarations.

## Commit Semantics
Reduction outputs are committed at deterministic commit points, using the same
ordering key as other authoritative writes:
- commit ordering key = (phase_id, task_id, sub_index)

## Cross-Reference
Reordering and commit ordering rules are defined in
`docs/arch/EXECUTION_REORDERING_POLICY.md`.
