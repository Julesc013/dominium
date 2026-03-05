Status: AUTHORITATIVE
Version: 1.0.0
Last Reviewed: 2026-03-06
Scope: STATEVEC-0 explicit state exposure for SYS/COMPILE/process capsules.

# Explicit State Vector Rule

## Purpose
Prevent hidden-state abstraction drift by requiring all output-affecting internal memory to be declared, versioned, serialized deterministically, and provenance-anchored.

## A) State Vector Definition
`StateVector` is the minimal sufficient set of variables that can influence:
- boundary outputs,
- collapse/expand correctness,
- compiled-model runtime behavior,
- process capsule continuation behavior.

Each owner (`system_id`, `process_id`, `compiled_model_id`) must reference a state vector definition describing fields and version.

## B) Sound Abstraction Rule
If a variable can change boundary outputs across ticks, it MUST be part of the declared state vector.

Corollaries:
- extension-only caches are allowed only when they cannot influence authoritative outputs,
- output-affecting memory outside the declared vector is a contract violation.

## C) Versioning and CompatX
State vectors are versioned by schema and owner definition:
- `version` identifies the state vector definition contract,
- migration behavior is explicit and deterministic,
- incompatible version restores must refuse with deterministic refusal code.

CompatX obligations:
- schema entries and supported versions must be declared,
- migrations are explicit or refusal-based, never silent.

## D) Zero-State Systems
A zero-memory owner is valid and may declare an empty `state_fields` list.

Rules:
- empty vector means no output-affecting memory exists,
- if any output-affecting state appears later, vector must be revised and versioned.

## E) Hidden State Prohibition
Prohibited:
- output-affecting owner state that is absent from its declared state vector,
- collapse/compile pathways that depend on undeclared mutable memory,
- restore paths that reconstruct behavior from undeclared side channels.

Enforcement:
- RepoX hard invariants,
- AuditX hidden-state smell analyzers,
- deterministic runtime guard in debug profiles that refuses unsafe collapse when undeclared output-affecting mutation is detected.

## Determinism Requirements
- stable field ordering during serialization,
- deterministic numeric normalization for state values (TOL discipline),
- deterministic hash anchoring of state snapshots,
- thread-count invariant replay outcomes for equivalent inputs.
