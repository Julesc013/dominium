--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- None. Engine provides generic primitives only if referenced.

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
# SPEC_PLAYER_CONTINUITY - Player Continuity and Seamless UX Contract

## 1) Scope
This spec defines the player-facing continuity contract. It governs UI behavior,
transitions, and presentation across local, planetary, system, galaxy, and
cosmos views without changing simulation semantics.

## 2) Core invariants
- UI/render are derived only; never authoritative.
- UI thread MUST NOT block on IO, decompression, or long computation.
- Time advances monotonically; UI must never present rewinds or pauses.
- Transitions must be continuous in presentation and input handling.
- Missing data degrades fidelity; it must never block presentation.

## 3) Disallowed player-visible states
The player must never observe:
- loading screens that freeze input or simulation
- unexplained teleports (instantaneous spatial jumps without transition cues)
- time stops or rewinds
- UI freezes caused by blocking work

## 4) Allowed transitions (presentation only)
- Zoom transitions between scale views (local → planet → system → galaxy → cosmos).
- Warp/transit visuals driven by transit state (e.g., tunnel/starfield).
- Gradual fidelity changes (placeholder → detailed) without stalling input.

## 5) State machine requirements
- UI state transitions are driven by input and snapshot availability only.
- UI state transitions must never change authoritative state.
- Transit state (if active) forces UI_TRANSIT presentation; exiting transit
  returns to the previous view.

## 6) Input continuity
- Input events are always accepted and routed during transitions.
- Input order is deterministic after platform normalization.
- UI-only remapping (e.g., camera controls in map views) is allowed and must not
  affect sim state.

## 7) Fidelity coupling
- Each view must render at every fidelity level.
- Low fidelity uses outlines/icons/text; high fidelity may add meshes/details.
- Fidelity changes must be smooth and must not trigger blocking loads.

## 8) Tests (normative)
Implementations must provide tests that validate:
- seamless traversal across all view scales without invalid UI states
- no frame stalls beyond the configured watchdog threshold
- input continuity during transitions
- placeholder rendering when derived data is missing
