# SPEC_ACTIONS — Intent → Action → Delta

This spec defines the deterministic command pipeline used by SIM.

## Scope
Applies to:
- intent ingestion from Dominium/UI/tools/agents
- validation and action compilation
- delta application as the only legal state mutation

## Pipeline (authoritative)
1. **Intent**
   - External deterministic command input for tick `N`.
   - Immutable and TLV-versioned (`docs/SPEC_PACKETS.md`).

2. **Validation**
   - Deterministic, side-effect free read of the current authoritative state.
   - Produces either rejection or one-or-more actions/deltas.

3. **Action**
   - Internal representation of a validated intent (optional encoding).
   - Immutable and deterministic.

4. **Delta**
   - The only mechanism that mutates authoritative simulation state.
   - Applied at defined commit points in the scheduler (`docs/SPEC_SIM_SCHEDULER.md`).

## Validation vs application
- Validation MUST NOT mutate state.
- Application MUST NOT perform validation-dependent branching that can diverge
  across peers; all required decisions MUST be encoded into deltas.

## Canonical ordering
- Intents are processed in canonical order.
- Deltas are applied in canonical order; tie-breaking by stable IDs.
- No pointer-order or hash-order behavior is permitted.

## Forbidden behaviors
- Direct mutation of engine state outside deltas (including UI-driven writes).
- Platform-dependent branching (time, threads, locale, filesystem enumeration).
- Tolerance/epsilon comparisons that can diverge across platforms.

## Source of truth vs derived cache
**Source of truth:**
- the delta stream committed each tick
- the authoritative state after delta commit

**Derived cache:**
- pre-validation indices or lookup caches used to validate efficiently
- action graphs built from intents (rebuildable)

## Related specs
- `docs/SPEC_DETERMINISM.md`
- `docs/SPEC_PACKETS.md`
- `docs/SPEC_SIM_SCHEDULER.md`
- `docs/SPEC_VM.md`

