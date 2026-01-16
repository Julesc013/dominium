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
# SPEC_FIDELITY_DEGRADATION — Derived Fidelity Ladder

## Scope
This spec defines how UI/render fidelity degrades when derived data is missing
or late. It applies to display-only behavior and MUST NOT affect simulation.

## Rules (mandatory)
- Fidelity changes MUST NOT mutate authoritative state.
- Missing derived data MUST lower fidelity rather than stall execution.
- The UI MUST render something at every fidelity level.
- Fidelity increases opportunistically when required derived data is ready.
- Fidelity changes MUST be independent of determinism hashes.

## Level guidance
Implementations SHOULD provide at least:
- **Low:** minimal UI and safe placeholders; no dependence on derived caches.
- **Medium:** partial overlays or debug layers that tolerate missing data.
- **High:** full visual overlays and derived cache usage.

These levels are derived-only and may vary per renderer, but MUST obey the
rules above.

## Related specs
- `docs/SPEC_NO_MODAL_LOADING.md`
- `docs/SPEC_STREAMING_BUDGETS.md`
