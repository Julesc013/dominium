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
# SPEC_TIME_FRAMES — Temporal Frames and Renderers

Status: draft
Version: 1

## Purpose
Define derived temporal frames over ACT. Frames are renderers; they never advance
independently and never modify ACT.

This spec is documentation-only. It introduces no runtime logic.

## Frames (required)

### Barycentric Sol Time (BST)
- Derived frame for the Sol system.
- Relativistic corrections modeled as offsets/functions.
- NEVER changes ACT.

### Galactic Coordinate Time (GCT)
- Milky Way-scale frame.
- Used for galactic events and epochs.
- NEVER changes ACT.

### Cosmological Proper Time (CPT)
- Universe-scale frame.
- Used only for epochs and deep time.
- NEVER changes ACT.

## Frame rules (mandatory)
- All frames are renderers over ACT.
- No frame advances independently.
- Frame conversion is deterministic and reversible where possible.
- Frames do not change causality.

## ASCII diagram

  ACT -> BST -> GCT -> CPT
    \-> calendar/clock renderers

## Examples
Positive:
- BST used for Sol system civil time rendering.
Negative (forbidden):
- Advancing BST independently of ACT.
- Per-region local clocks.

## References
- docs/specs/SPEC_STANDARDS_AND_RENDERERS.md
- docs/specs/SPEC_TIME_CORE.md
- docs/specs/SPEC_CALENDARS.md
- docs/specs/SPEC_INFORMATION_MODEL.md
- docs/specs/SPEC_EFFECT_FIELDS.md

## Test and validation requirements (spec-only)
- Frame conversion determinism tests
- Round-trip frame rendering tests