# SPEC_TIME_CORE — Canonical Time Model

Status: draft
Version: 1

## Purpose
Define the authoritative time model. Time is real and continuous; calendars are
interfaces. Physics time is authoritative and monotonic.

This spec is documentation-only. It introduces no runtime logic.

## Core axioms (locked)
- Time is real and continuous; calendars are interfaces.
- Physics time is authoritative and monotonic.
- Calendars, clocks, and dates NEVER affect physics.
- Leap seconds never exist in the simulation core.
- Relativity is modeled, never patched.
- Knowledge of time is diegetic and gated.
- Different actors may legitimately disagree on time/date.
- At larger scales, calendars collapse into duration/epochs.
- Everything must round-trip deterministically.

## Canonical time model (authoritative)

### Atomic Continuous Time (ACT)
- Canonical physical time.
- SI seconds.
- Monotonic.
- Stored as fixed-point or int64.
- The ONLY authoritative time variable.

### Representation
ACT is represented by:
- tick_index (u64)
- ups (u32, ticks per second)

Conversion is deterministic and integer-only. ACT never uses leap seconds.

## World instantiation and start state
- Each world/universe has its own ACT epoch and pinned constants.
- Worlds do NOT share a global "game start."

Default reference world:
- Civil anchor: Gregorian Jan 1, 2000 AD (renderer only).
- Immediately converted to ACT/BST; Gregorian is a renderer thereafter.

Spawn time:
- Player spawns at local sunrise (solar altitude = 0 deg).
- If undefined, deterministic fallback:
  - solar max/min
  - terminator midpoint
  - station-defined light cycle

## Implementation notes (engine)
Engine provides:
- ACT storage and monotonic advancement
- deterministic ACT arithmetic with explicit overflow behavior
- pure frame conversion hooks (BST/GCT/CPT)
- time event scheduling primitives (see `docs/SPEC_EVENT_DRIVEN_STEPPING.md`)

Engine does NOT provide:
- calendars or formatting
- locale or standards resolution
- UI hooks

### Batch invariance (proof sketch)
ACT advancement uses integer arithmetic with no side effects.
Advancing by N seconds once yields the same ACT as advancing by 1 second N times
because addition is associative and monotonic and refuses backward movement.

### Overflow behavior
- ACT arithmetic checks bounds and returns overflow errors on saturation risk.
- Overflow is never silent.

### Engine/game boundary
- Engine owns ACT and event queue mechanics.
- Game interprets frames/calendars and schedules gameplay events.

## Prohibitions (enforced)
- Leap seconds in ACT/BST/GCT/CPT.
- Stored formatted dates in authoritative state.
- Calendar math in the engine.
- Implicit time standards.
- Time affecting causality.

Leap seconds are allowed only as a display layer for UTC compatibility using
external, versioned leap tables. They MUST NOT affect scheduling or simulation.

## ASCII diagram

  ACT (authoritative) -> Frames (BST/GCT/CPT) -> Calendars/Clocks -> UI

## Examples
Positive:
- ACT tick_index + ups used for scheduling and simulation.
Negative (forbidden):
- Storing "2025-01-01" as authoritative time.
- Adjusting ACT for leap seconds.

## References
- docs/SPEC_STANDARDS_AND_RENDERERS.md
- docs/SPEC_TIME_FRAMES.md
- docs/SPEC_CALENDARS.md
- docs/SPEC_TIME_STANDARDS.md
- docs/SPEC_INFORMATION_MODEL.md
- docs/SPEC_EFFECT_FIELDS.md

## Test and validation requirements (spec-only)
- ACT monotonicity tests
- Frame conversion determinism tests
- Leap second exclusion tests
