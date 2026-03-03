# Physics Proof and Replay Hooks

Status: CANONICAL
Last Updated: 2026-03-04
Scope: PHYS-0 proof/replay expectation contract for physics exceptions.

## 1) Artifact Family Classification

`exception_event` is a canonical META-INFO artifact of family `RECORD`.

Classification rationale:

- it records factual invariant-exception deltas
- it is provenance-bearing and replay-relevant
- it is not an interpreted belief/report artifact

## 2) Proof Bundle Expectation

When one or more `exception_event` rows exist in a proof window:

- proof bundles must include deterministic witness coverage for those rows
- coverage may be carried via explicit fields in a future schema revision or via deterministic extension keys in v1.0.0 (`extensions` open map)
- witness coverage must include exception ordering and deterministic fingerprints

Minimum expectation key for v1.0.0 extensions:

- `extensions.physics_exception_event_hash_chain`

## 3) Replay/Reenactment Expectation

Reenactment windows must reproduce exception behavior deterministically:

- identical `exception_id` ordering for equivalent inputs
- identical `exception_kind`, `affected_quantities`, and `reason_code`
- identical deterministic fingerprints for the same authoritative window

Any mismatch is replay drift and must be treated as a determinism failure.

## 4) Non-Goals (PHYS-0)

- no runtime proof-bundle schema field expansion in this phase
- no new solver behavior
- no wall-clock-dependent replay semantics
