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
# SPEC_FIDELITY_PROJECTION — Fidelity Projection Engine Canon

Status: draft
Version: 1

## Purpose
Define the canonical Fidelity Projection Engine (FPE): the deterministic system
that controls how simulation fidelity scales up and down across space, time,
population, economy, and player focus — without fabricating entities or breaking
continuity.

This spec is documentation-only. It introduces no runtime logic.

## Core axioms (locked)
1) Fidelity change NEVER creates or destroys reality.
2) Fidelity change is deterministic and auditable.
3) Fidelity change preserves conserved quantities.
4) Fidelity change preserves provenance.
5) Fidelity change is hysteretic (no thrashing).
6) Fidelity change is interest-driven, not view-driven.
7) Fidelity change cost is bounded.
8) Fidelity change works identically in SP and MMO.
9) Fidelity change integrates with time warp.
10) Fidelity change never alters authoritative clocks.

## Definitions

### Fidelity tiers
- MACRO
- MESO
- MICRO
- FOCUS

### Macro state
Aggregated, always-on state. Examples:
- population cohorts
- aggregate inventories
- production/consumption rates
- job backlogs
- next_due_tick

### Meso state
Structured machines. Examples:
- cities
- factories
- organizations
- trade routes

### Micro state
Concrete entities. Examples:
- individual people
- vehicles
- machines
- buildings

### Focus state
Player-interactive subset of micro. Full animation and input.

## Refinement and collapse (mandatory)

### Refinement (MACRO/MESO -> MICRO)
Deterministically instantiate entities from aggregates.
Inputs:
- aggregate state
- deterministic seed (derived from IDs + ACT)
- projection reason
Outputs:
- concrete entities with stable IDs

No RNG. No invention.

### Collapse (MICRO -> MACRO/MESO)
Deterministically merge entities back. Preserve:
- counts
- inventories
- obligations
- job progress
- provenance hashes

Special entities may be pinned.

## Interest sets (mandatory)
Interest is the ONLY driver of fidelity. Interest sources include:
- player focus
- delivered commands
- active logistics routes
- sensors and comm coverage
- hazards and conflicts
- governance scope

Render distance is NOT sufficient.

## Hysteresis rules (mandatory)
Define:
- stricter thresholds for refine than collapse
- time-based dampening
- explicit pin rules for:
  - named persons
  - mission-critical entities
  - visible entities in LOS

## Engine vs game responsibilities

Engine (Domino, C89/C90) MAY:
- provide deterministic ID generation
- provide aggregation helpers
- provide event scheduling

Engine MUST NOT:
- know fidelity tiers
- spawn entities
- collapse entities

Game (Dominium, C++98) MUST:
- manage fidelity state
- perform refine/collapse
- manage interest sets
- ensure LOS continuity
- emit audit records

## Continuity guarantees (mandatory)
- If an entity is visible and relevant, it cannot disappear.
- Leaving relevance collapses deterministically, not deletes.
- Returning to relevance recreates the same entities.
- Assets and obligations are conserved.

## Examples (mandatory)

### 1) Early-game village fully micro-simulated
Interest set includes the village; fidelity remains MICRO/FOCUS.

### 2) Mid-game city collapsing to meso
Interest drops below refine threshold; city collapses to MESO while preserving
counts, inventories, and obligations.

### 3) Late-game megacity aggregated to macro
Interest minimal; aggregate state stores production rates and job backlogs.

### 4) Player travels away and returns
Interest recovers; refinement recreates the same entities deterministically.

### 5) MMO shard transfer without discontinuity
Aggregate state and provenance hashes transfer; refinement yields consistent
entities on the new shard.

## Integration points (mandatory)
- Effect fields (EF*)
- Command and Doctrine (CMD*)
- Information & Belief Model (INF*)
- Economy and Ledger (E*)
- Time warp (TW*)
- World Source Stack (WSS*)

## Prohibitions (enforced)
- Chunk-based simulation
- Render-distance-based despawn
- Random entity selection
- Lossy aggregation
- Special-casing early game
- "Fake" background simulation

## References
- Information model: `docs/SPEC_INFORMATION_MODEL.md`
- Command intent: `docs/SPEC_COMMAND_MODEL.md`
- Effect fields: `docs/SPEC_EFFECT_FIELDS.md`
- World source stack: `docs/SPEC_WORLD_SOURCE_STACK.md`

## Test and validation requirements (spec-only)
Implementations must provide:
- refinement/collapse reversibility tests
- conservation tests
- hysteresis stability tests
- LOS continuity tests
- MMO shard handoff tests
- time warp interaction tests
