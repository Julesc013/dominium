Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Future Phase Guidelines (LIFE/CIV Safe Extension)

Status: active
Version: 1

These rules define how to extend LIFE/CIV systems without breaking determinism,
scalability, or epistemic boundaries.

## Non-Negotiable Rules
- New simulation work MUST be event-driven and expose `next_due_tick`.
- No subsystem may iterate over global populations, cities, or markets.
- Provenance MUST exist for any object that appears in the world.
- UI/tools MUST use capability snapshots and epistemic interfaces only.
- No OS time, non-deterministic RNG, or float math in authoritative code.
- Rendering MUST remain non-authoritative and isolated to `engine/render/**`.

## Schema and Validation Requirements
- Every new schema MUST define Status + Version and follow DATA0 rules.
- Major schema changes MUST ship migrations or refuse load.
- Unbounded collections are FORBIDDEN; define explicit max sizes.
- New schema fields MUST document determinism and performance impact.
- Validators MUST be updated with new rule IDs in `docs/CI_ENFORCEMENT_MATRIX.md`.

## Test and CI Requirements
- Every new subsystem MUST add:
  - deterministic ordering tests
  - batch vs step equivalence tests
  - epistemic gating tests (if UI-visible)
  - scale/boundedness tests
- New tests MUST be registered in CTest and referenced in the CI matrix.
- Any exception to determinism/performance law MUST be documented and audited.

## Extending LIFE
- Death, birth, continuation, and remains MUST remain causal and schedulable.
- Heir/authority selection MUST remain bounded and deterministic.
- No respawn or fabricated population without explicit causal pipelines.
- Knowledge of life events MUST propagate through sensors/communications only.

## Extending CIV
- Population growth, migration, and production MUST remain flow-based.
- Institutions MUST be constructed and governed by explicit legitimacy rules.
- Technology diffusion MUST remain epistemic and scheduled.
- Interplanetary/stellar logistics MUST remain logical (no global physics).

## Interaction Rules
- Cross-system links MUST be explicit and auditable.
- Ledger interactions MUST conserve balances; no implicit transfers.
- Interest sets determine activation; camera/UI state never does.

## Required Documentation Updates
- Update or add SPEC_* docs for any new subsystem.
- Update `docs/ci/DETERMINISM_TEST_MATRIX.md` fixtures.
- Update `docs/CI_ENFORCEMENT_MATRIX.md` with new IDs and enforcement stages.
- Update audit docs if Phase 6 guarantees are affected.