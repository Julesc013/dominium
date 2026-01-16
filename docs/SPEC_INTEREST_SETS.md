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
# SPEC_INTEREST_SETS — Interest Sets & Relevance Scheduler Canon

Status: draft
Version: 1

## Purpose
Define the canonical Interest Sets & Relevance Scheduler: the deterministic
mechanism that decides what parts of the world are active, at what fidelity,
and why — without iterating over the entire universe or relying on render distance.

This spec is documentation-only. It introduces no runtime logic.

## Core axioms (locked)
1) Relevance drives simulation; irrelevance is latent.
2) Interest Sets are explicit and enumerable.
3) No simulation occurs without interest.
4) Interest changes are deterministic and auditable.
5) Relevance is not the same as visibility.
6) Relevance changes respect hysteresis.
7) Interest never fabricates state.
8) Interest is orthogonal to fidelity.
9) Interest evaluation cost is bounded.
10) Removing interest eventually collapses fidelity.

## Definitions

### Interest set
A deterministic set of references indicating relevance. Elements may include:
- entities
- locations
- regions
- routes
- contracts
- organizations

Each element has:
- interest_reason
- interest_strength
- expiry conditions

### Interest source
A system that produces interest. Examples:
- player focus
- active commands
- logistics routes
- sensor coverage
- communication endpoints
- hazards/conflicts
- governance scope

### Relevance state
A classification derived from interest:
- HOT (focus/micro)
- WARM (meso)
- COLD (macro)
- LATENT (seed only)

### Relevance transition
A deterministic change in relevance state. May trigger:
- refinement
- collapse
- caching
- scheduling

## Interest evaluation pipeline (mandatory)

ASCII diagram:

  [ Interest Sources ]
          |
          v
  [ Interest Aggregation ]
          |
          v
  [ Relevance Classification ]
          |
          v
  [ Fidelity Projection Requests ]
          |
          v
  [ Simulation Scheduling ]

No step may iterate globally.

## Interest sources (mandatory enumeration)
At minimum:

1) Player focus
   - camera
   - controlled entities
   - selected UI targets

2) Command activity
   - pending CommandIntents
   - executing commands
   - abort conditions

3) Logistics
   - active transport routes
   - shipments in transit

4) Sensors and comms
   - observation coverage
   - message endpoints

5) Hazards and conflicts
   - combat
   - disasters
   - effect-field extremes

6) Governance
   - jurisdictional control
   - taxation scope
   - law enforcement

Each source must produce bounded interest and include expiry semantics.

## Hysteresis rules (mandatory)
Define:
- enter thresholds > exit thresholds
- time-based dampening
- pinning rules for:
  - visible entities
  - named entities
  - mission-critical entities

Hysteresis must prevent thrashing, preserve continuity, and be deterministic.

## Engine vs game responsibilities

Engine (Domino, C89/C90) MAY:
- provide deterministic containers
- provide set operations
- provide scheduling primitives

Engine MUST NOT:
- decide relevance
- manage interest lifetimes
- know about players or UI

Game (Dominium, C++98) MUST:
- collect interest from sources
- aggregate interest deterministically
- classify relevance states
- request fidelity changes
- manage scheduling accordingly

## Relevance and fidelity interaction
- Relevance requests refinement (see `docs/SPEC_FIDELITY_PROJECTION.md`).
- Loss of relevance triggers collapse.
- Relevance interacts with:
  - time warp
  - communication
  - economy
  - governance

Relevance must not mutate world state or override fidelity invariants.

## Performance requirements
- Upper bounds on interest set size.
- O(1) or O(log n) operations per interest change.
- No per-tick scanning of interest sets.
- Lazy evaluation and expiry.

## Prohibitions (enforced)
- Chunk grids
- Distance-only relevance
- Render-driven activation
- Global "update all" loops
- Non-auditable heuristics

## Examples (mandatory)

### 1) Single player farming one plot on Earth
Interest sources: player focus + local commands.
Relevance: local HOT, nearby WARM, rest LATENT.
Fidelity: local MICRO/FOCUS, rest MACRO/LATENT.

### 2) Logistics convoy crossing interplanetary space
Interest sources: active route + shipments.
Relevance: route WARM, endpoints WARM, unrelated regions COLD/LATENT.
Fidelity: route meso; endpoints meso/micro depending on local interest.

### 3) Distant war
Interest sources: governance + hazards/conflicts.
Relevance: conflict region WARM, adjacent regions COLD.
Fidelity: meso in conflict region, macro elsewhere.

### 4) Player opens map of another planet
Interest sources: UI target (ephemeral).
Relevance: target region COLD/WARM depending on policy.
Fidelity: no micro refine; macro/meso summaries only.

### 5) MMO shard handoff
Interest sources: governance scope + command routes.
Relevance: migrating region HOT/WARM during handoff.
Fidelity: refined as needed, then collapsed deterministically.

## References
- Fidelity projection: `docs/SPEC_FIDELITY_PROJECTION.md`
- Provenance: `docs/SPEC_PROVENANCE.md`
- Information model: `docs/SPEC_INFORMATION_MODEL.md`

## Test and validation requirements (spec-only)
Implementations must provide:
- interest aggregation determinism tests
- hysteresis stability tests
- relevance/fidelity interaction tests
- performance bounding tests
- MMO consistency tests
