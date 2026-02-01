Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- Deterministic primitives and invariants defined by this spec.
- Implementation lives under `engine/` (public API in `engine/include/`).

GAME:
- Rules, policy, and interpretation defined by this spec.
- Implementation lives under `game/` (rules/content/ui as applicable).

TOOLS:
- None. Tools may only consume public APIs if needed.

SCHEMA:
- None (no canonical schema formats defined here).

FORBIDDEN:
- No launcher/setup orchestration logic in engine or game.
- No engine internal headers exposed outside engine targets.
- No game rules or policy implemented inside engine primitives.

DEPENDENCIES:
- Engine -> libs/ and schema/ only (never game/launcher/setup/tools).
- Game -> engine public API and schema/ only.
- Tools -> engine public API, game public API, and schema/ only.
- Launcher/Setup (if applicable) -> libs/contracts + schema (launcher may also use engine public API).
--------------------------------
# SPEC_STREAMING_BUDGETS — Derived Work Budgets

## Scope
This spec defines budgeted execution for derived (non-authoritative) work in
the game runtime, including IO, decompression, and cache/build steps.

## Budget types
Each derived pump cycle MUST obey all applicable budgets:
- **Time budget:** maximum wall-clock time per pump (milliseconds).
- **IO budget:** maximum bytes of IO work attributed to the pump.
- **Job budget:** maximum number of jobs processed per pump.

## Rules (mandatory)
- Derived work MUST be processed only within explicit budgets.
- If the next job does not fit the remaining budget, it MUST remain pending.
- Derived jobs MAY supply budget hints; hints are advisory and MUST NOT affect
  authoritative state.
- Cancellation and deferral MUST NOT affect determinism.
- Job selection order MUST be deterministic (priority, then submit order).
- Budget exhaustion MUST NOT block the UI/render thread.

## Integration requirements
- Budget values are configurable and SHOULD have finite defaults.
- Budgets are independent of authoritative simulation cadence.
- Derived work completion order MUST NOT affect simulation hashes.

## Related specs
- `docs/specs/SPEC_NO_MODAL_LOADING.md`
- `docs/specs/SPEC_FIDELITY_DEGRADATION.md`