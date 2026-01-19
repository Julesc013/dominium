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
# SPEC_TIME_KNOWLEDGE — Diegetic Time and Epistemic Gating

Status: draft  
Version: 1

## Purpose
Define how time knowledge is acquired, gated, and represented. Time knowledge is
diegetic, uncertain, and actor-specific. It never alters authoritative ACT.

## Core rules
- Actors may start with no clock and no calendar.
- Time knowledge is granted only via devices, documents, or institutions.
- HUD time is diegetic: remove a device -> time becomes UNKNOWN.
- Drift and uncertainty are deterministic; no RNG.
- Conflicts between clocks are visible and must not be auto-resolved.

## Time knowledge pipeline

  ACT (engine) -> Frame conversion -> Clock device output
       -> Effect fields -> Time knowledge update -> Belief store -> UI

No other path to time knowledge is allowed.

## Data model
### Time knowledge state (per actor/faction)
- known_frames_mask (ACT/BST/GCT/CPT)
- known_calendars (IDs)
- known_clocks (clock IDs)
- uncertainty envelope per clock
- last calibration tick per clock

The state does NOT store ACT itself. It stores only epistemic artifacts.

### Clock device
A clock is a deterministic source of time information with explicit limits.

Clock device fields:
- reference frame
- base accuracy (seconds)
- drift rate (ppm)
- calibration requirements
- failure modes (power loss, damage, jamming)

Clock taxonomy (minimum set):
- sundial
- mechanical clock
- quartz clock
- atomic clock
- network time feed
- astronomical observation

### Time document
Time documents grant knowledge of standards, not live time:
- calendars
- ephemerides
- almanacs

Documents never create time readings.

## Drift & uncertainty
Drift is deterministic and based on:
- elapsed ACT since last calibration
- device drift rate
- effect-field degradation
- damage and power state

Uncertainty widens over ACT and never collapses without calibration or
explicit observation. Unknown is returned when a device cannot produce a
reading.

## Calibration
Calibration is an explicit action that:
- resets drift accumulation
- reduces uncertainty
- consumes time/resources (game-layer)
- produces an audit record

Calibration does not change ACT and does not synchronize other devices unless
explicitly commanded.

## Multiple clocks & disagreement
- Multiple clocks may exist per actor.
- Conflicting readings are displayed side-by-side.
- The player or UI selects which clock to trust.
- No implicit reconciliation is permitted.

## Failure & loss modes
- Destruction -> clock removed -> UNKNOWN time
- Power loss -> reading unavailable or downgraded
- Isolation -> drift accumulates deterministically
- Jamming -> clock output becomes UNKNOWN

## Examples
Starting with no clock:
- No devices -> UI shows UNKNOWN for time.

Losing a watch:
- Remove device -> time readings disappear immediately.

Syncing via radio:
- Network time feed reduces uncertainty after calibration.

Clocks drifting apart:
- Two clocks with different drift rates show different times; both are visible.

## Prohibitions
- Implicit time knowledge
- Automatic synchronization
- OS time usage
- Calendar math in the knowledge layer
- UI time display without a clock

## Test requirements (spec-only)
- No clock -> UNKNOWN time
- Drift accumulation correctness
- Calibration reduces uncertainty
- Device damage effects
- Multiple clock disagreement
- Deterministic behavior across replay

## References
- `docs/SPEC_STANDARDS_AND_RENDERERS.md`
- `docs/SPEC_INFORMATION_MODEL.md`
- `docs/SPEC_EPISTEMIC_GATING.md`
- `docs/SPEC_TIME_STANDARDS.md`
- `docs/SPEC_EFFECT_FIELDS.md`
