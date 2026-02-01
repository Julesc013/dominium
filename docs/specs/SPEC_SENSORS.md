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
# SPEC_SENSORS — Sensors and Observation Pipeline Canon

Status: draft
Version: 1

## Purpose
Define the canonical Sensors & Observation system: the deterministic mechanism by
which authoritative world state produces InfoRecords for actors.

This spec is documentation-only. It introduces no runtime logic.

## Core axioms (locked)
1) Observation is discrete and scheduled.
2) Sensors are the ONLY source of new information.
3) Sensors produce InfoRecords, not truth.
4) Observation never modifies world state.
5) Sensors have cadence, range, resolution, and cost.
6) Sensors are affected by effect fields.
7) Sensors can fail, degrade, or be destroyed.
8) No sensor has infinite range or precision.
9) Observation is deterministic and replayable.
10) Removing a sensor removes its future contributions.

## Definitions

### Sensor
A deterministic information-producing component bound to:
- an entity (person, vehicle, structure), or
- a location (site, region)

Each sensor declares:
- sensing domain
- range
- resolution tier
- cadence
- susceptibility to effects
- operating cost

### Sensing domain
The category of facts a sensor can observe.
Examples: visual, radar, radio, seismic, chemical, economic, temporal, social.

### Cadence
The schedule on which a sensor produces observations. Defined in ACT ticks.
Sensors do NOT run continuously.

### Observation event
A scheduled sensing action that:
- samples authoritative state
- applies effect field filters
- produces zero or more InfoRecords

## Observation pipeline (mandatory)

ASCII diagram:

  [ Authoritative World State ]
            |
            v  (sample)
  [ Sensor Capabilities ]
            |
            v  (filter)
  [ Effect Fields (Perception) ]
            |
            v  (schedule/limit)
     [ Observation Event ]
            |
            v  (construct)
     [ InfoRecord Creation ]
            |
            v
    [ Belief Store Merge ]

Each step is deterministic and auditable.

## Sensor properties (mandatory)
Every sensor MUST declare:
- RANGE (geometric, topological, or graph-based)
- RESOLUTION TIER (maximum possible tier)
- CADENCE (fixed or conditional, e.g. "only when powered")
- COST (power, labor, attention, risk)
- SUSCEPTIBILITY (which effect fields degrade it)
- FAILURE MODES (damaged, jammed, misaligned, uncalibrated)

## Engine vs game responsibilities

Engine (Domino, C89/C90) MAY:
- expose read-only accessors for authoritative facts
- provide deterministic math helpers
- provide hooks for observation scheduling

Engine MUST NOT:
- schedule sensors
- create InfoRecords
- know about actors or belief

Game (Dominium, C++98) MUST:
- register sensors
- schedule observation events
- apply effect field filters
- create InfoRecords
- merge into BeliefStores

## Resolution and degradation
Sensor maximum resolution is:
- capped by design
- degraded by distance
- degraded by effect fields
- degraded by damage or lack of calibration

UNKNOWN is produced when:
- out of range
- blocked
- jammed
- insufficient resolution

No "best guess" unless explicitly encoded as a bounded interval.

## Types of sensors (minimum set)
Each type produces InfoRecords and integrates with effect fields.

- Visual sensors
- Radar/Lidar
- Passive radio
- Active comm interception
- Seismic/structural
- Environmental (atmospheric)
- Economic sensors (prices, supply)
- Time sensors (clocks)
- Social sensors (reports, rumors)

## Cost and tradeoffs (mandatory)
- Sensors consume resources.
- High cadence reduces coverage elsewhere.
- Sensors expose the observer to risk (e.g., emissions).
- Sensor networks require logistics and maintenance.

Sensing is gameplay, not free omniscience.

## Prohibitions (enforced)
- Vision cones tied to rendering
- Instant knowledge on proximity
- Global map reveals
- Random sensing noise
- Sensors bypassing effect fields
- Sensors auto-updating belief without events

## Integration points (mandatory)
- Information model: `docs/specs/SPEC_INFORMATION_MODEL.md`
- Effect fields: `docs/specs/SPEC_EFFECT_FIELDS.md`
- Communication (future spec)
- Epistemic UI layer
- Command intent system
- Time warp (cadence invariance under warp)

## Worked examples

### Map uncertainty
A visual sensor detects an entity at COARSE resolution. InfoRecords indicate
"exists in area," not a precise position. Map UI shows a region marker.

### Sensor degradation
A radar sensor with maximum BOUNDED resolution is degraded by distance and
effect fields to COARSE. The InfoRecord is created at COARSE tier.

### Jammed sensor
An effect field marks the sensor as jammed. Observation event produces UNKNOWN
InfoRecords with a "jammed" reason.

### Economic quote delay
An economic sensor observes market quotes at cadence N ticks. The InfoRecord
arrives with ACT timestamp and decay parameters; newer quotes do not delete older
ones automatically.

## Test and validation requirements (spec-only)
Implementations must provide:
- deterministic observation tests
- cadence invariance under time warp
- effect-field degradation tests
- sensor removal tests (source gone -> no new records)
- lockstep/server-auth parity tests