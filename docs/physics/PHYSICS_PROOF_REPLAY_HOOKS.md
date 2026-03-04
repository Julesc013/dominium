# Physics Proof and Replay Hooks

Status: CANONICAL
Last Updated: 2026-03-04
Scope: PHYS-0 proof/replay expectation contract for physics exceptions.

## 1) Artifact Family Classification

`exception_event` is a canonical META-INFO artifact of family `RECORD`.
`entropy_event` and `entropy_reset_event` are canonical META-INFO artifacts of family `RECORD`.

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

PHYS-3 adds deterministic energy witnesses:

- `energy_ledger_hash_chain`
- `boundary_flux_hash_chain`

When `energy_ledger_entry` or `boundary_flux_event` rows are present in the authoritative window,
proof bundles must carry both chains.

PHYS-4 adds deterministic entropy witnesses:

- `entropy_hash_chain`
- `entropy_reset_events_hash_chain`

When entropy contribution/reset rows are present in the authoritative window,
proof bundles must carry both entropy chains.

## 3) Replay/Reenactment Expectation

Reenactment windows must reproduce exception behavior deterministically:

- identical `exception_id` ordering for equivalent inputs
- identical `exception_kind`, `affected_quantities`, and `reason_code`
- identical deterministic fingerprints for the same authoritative window

Any mismatch is replay drift and must be treated as a determinism failure.

For PHYS-3 energy accounting, reenactment windows must also reproduce:

- identical ordered `energy_ledger_entries`
- identical ordered `boundary_flux_events`
- identical `energy_ledger_hash_chain`
- identical `boundary_flux_hash_chain`

Verification helpers:

- `tools/physics/tool_verify_energy_conservation`
- `tools/physics/tool_replay_energy_window`

For PHYS-4 entropy accounting, reenactment windows must also reproduce:

- identical ordered `entropy_event_rows`
- identical ordered `entropy_reset_events`
- identical `entropy_hash_chain`
- identical `entropy_reset_events_hash_chain`

For momentum replay consistency (PHYS-1 substrate), reenactment windows must reproduce:

- identical ordered `momentum_states`
- identical ordered `impulse_application_rows`
- identical `momentum_hash_chain`
- identical `impulse_event_hash_chain`

Verification helper:

- `tools/physics/tool_replay_momentum_window`

## 4) Non-Goals (PHYS-0)

- no runtime proof-bundle schema field expansion in this phase
- no new solver behavior
- no wall-clock-dependent replay semantics
