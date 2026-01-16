--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- None. Engine provides generic primitives only if referenced.

GAME:
- Rules, policy, and interpretation defined by this spec.
- Implementation lives under `game/` (rules/content/ui as applicable).

TOOLS:
- Authoring/inspection utilities described here.
- Implementation lives under `tools/` (including shared tool runtime).

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
Status: draft
Version: 1

## Purpose
Define the Epistemic Interface Layer (EIL): the only interface by which UI/HUD
systems may access information. UI consumes knowledge, not authoritative state.

This spec is documentation-only. It introduces no runtime logic.

## Core axioms (locked)
1) UI sees only what an actor knows.
2) All UI-visible data originates from BeliefStores.
3) UI never queries authoritative state.
4) UI never invents information.
5) UI shows uncertainty explicitly.
6) UI respects latency and staleness.
7) UI behavior is deterministic.
8) Removing a knowledge source removes UI data.
9) Diegetic and HUD UI are projections of the same data.
10) UI changes never affect simulation.

## Definitions

### Epistemic Interface Layer (EIL)
A read-only projection of an actor's BeliefStore. EIL outputs capability
objects, not raw facts. It is deterministic per ACT tick.

### Capability
A structured description of what information is available. Each capability
MUST include:
- capability_id
- subject
- resolution tier
- uncertainty envelope
- latency
- source provenance
- expiry/staleness info

### Capability snapshot
The set of all capabilities available to an actor at a given ACT tick.
Snapshots are deterministic and replayable.

### Projection
A pure transformation:

    Capability Snapshot -> UI Elements

Projections can be diegetic or non-diegetic but must not alter capability data.

## Capability categories (mandatory)
Capabilities must be derived only from BeliefStores and must degrade to UNKNOWN.
At minimum, the following categories are required:
- TIME_READOUT
- CALENDAR_VIEW
- MAP_VIEW
- POSITION_ESTIMATE
- HEALTH_STATUS
- INVENTORY_SUMMARY
- ECONOMIC_ACCOUNT
- MARKET_QUOTES
- COMMUNICATIONS
- COMMAND_STATUS
- ENVIRONMENTAL_STATUS
- LEGAL_STATUS

Each capability class MUST declare required knowledge sources and its UNKNOWN
fallback behavior.

## Capability generation pipeline (mandatory)
Pipeline order is fixed and must not access authoritative state:

  [ Belief Store (INF0) ]
              |
              v
  [ Capability Derivation Rules ]
              |
              v
  [ Effect Field Filters (perception) ]
              |
              v
  [ Capability Snapshot ]
              |
              v
  [ UI Projections ]

No step may be skipped or merged.

## Engine vs game responsibilities

Engine (Domino, C89/C90):
- Provides no UI-facing APIs.
- Has no knowledge of EIL.

Game (Dominium, C++98):
- Builds capability snapshots.
- Applies epistemic rules and effect-field filters.
- Exposes read-only EIL API to UI.

## Diegetic vs non-diegetic UI

Diegetic UI:
- Projections anchored to in-world devices.
- Removing the device removes the capability.

Non-diegetic HUD:
- Screen-space projection of the same capability.
- Optional, configurable, removable.

Both must show identical uncertainty, latency, and staleness.

## Customization and modding
- Capability list is fixed by simulation.
- UI may choose which capabilities to display and how to project them.
- UI may NOT request new capabilities or bypass gating.

This enables HUD customization without granting new knowledge.

## Spectator and replay
- Spectator capability sets are determined by explicit permissions.
- Replay uses recorded BeliefStores to reproduce capability snapshots.
- No omniscient spectator mode unless explicitly granted.

## Accessibility and debug UI
- Accessibility overlays are projections of capabilities, not new data.
- Debug UI uses privileged capability sets that must be explicit and auditable.

## Prohibitions (enforced)
- UI querying authoritative world state.
- UI-side simulation or hidden queries.
- Implicit defaults when data is UNKNOWN.
- Silent capability grants.
- UI-only logic branches that affect gameplay.

## Positive examples

### No clock -> no time UI
If the actor has no time device, TIME_READOUT capability is UNKNOWN and time UI
elements render as UNKNOWN or are hidden.

### Delayed map updates
MAP_VIEW capability shows stale positions with explicit timestamps and degraded
resolution after communication latency.

### Conflicting market quotes
MARKET_QUOTES capability includes multiple sources with differing values and
uncertainty envelopes; UI displays conflict, not a merged "truth".

### Device loss removing HUD elements
Removing a sensor device removes ENVIRONMENTAL_STATUS capability; HUD elements
disappear or show UNKNOWN.

## Negative examples (forbidden)
- "UI reads world position directly for minimap."
- "HUD shows exact time without a clock device."
- "Spectator always sees the full world."
- "UI resolves conflicting sources silently."

## Integration points
- `docs/SPEC_INFORMATION_MODEL.md`
- `docs/SPEC_SENSORS.md`
- `docs/SPEC_COMMUNICATION.md`
- `docs/SPEC_TIME_KNOWLEDGE.md`
- `docs/SPEC_EFFECT_FIELDS.md`

## Test and validation requirements (spec-only)
Implementations must provide:
- capability derivation determinism tests
- gating removal tests (source removed -> capability removed)
- latency and staleness tests
- replay equivalence tests
- spectator permission tests
