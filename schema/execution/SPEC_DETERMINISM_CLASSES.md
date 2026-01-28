# SPEC_DETERMINISM_CLASSES (EXEC0)

Status: binding.
Scope: determinism classes for TaskNode execution behavior.
Non-goals: backend scheduling algorithms.

## Purpose
Determinism classes define which reorderings are allowed while preserving
authoritative determinism and replay fidelity.

## Classes

### STRICT
- Bit-identical results required.
- No reordering unless proven safe and identical.
- Parallelism allowed only when results are provably identical.
- If multiple tasks are eligible, commit order MUST follow the canonical
  ordering key.

### ORDERED
- Deterministic ordering required.
- Parallelism allowed only within a fixed, deterministic order.
- Reduction order MUST be stable and explicitly declared.
- Total order ties are broken by the canonical ordering key.

### COMMUTATIVE
- Reordering allowed if reduction rules are satisfied.
- Only permitted when all writes/reductions are commutative and deterministic.
- Floating-point reductions in AUTHORITATIVE tasks are forbidden.
- Reductions MUST use fixed-tree deterministic reduction.

### DERIVED
- Non-authoritative; must not affect authoritative state or sim hash.
- May be reordered freely as long as it remains derived-only.

## Global Rules
- Every TaskNode MUST declare exactly one determinism class.
- determinism_class MUST NOT change at runtime.
- determinism_class MUST be consistent with the TaskNode category.
- Reordering is forbidden unless the determinism class explicitly permits it.

## Policy References
- Reordering and commit ordering: `docs/architecture/EXECUTION_REORDERING_POLICY.md`
- Deterministic reductions: `docs/architecture/DETERMINISTIC_REDUCTION_RULES.md`
