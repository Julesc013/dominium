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
- docs/SPEC_STANDARDS_AND_RENDERERS.md
- docs/SPEC_TIME_CORE.md
- docs/SPEC_CALENDARS.md
- docs/SPEC_INFORMATION_MODEL.md
- docs/SPEC_EFFECT_FIELDS.md

## Test and validation requirements (spec-only)
- Frame conversion determinism tests
- Round-trip frame rendering tests
