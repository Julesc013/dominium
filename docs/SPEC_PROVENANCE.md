# SPEC_PROVENANCE — Provenance & Construction Law Canon

Status: draft
Version: 1

## Purpose
Define the canonical Provenance & Construction Law: the deterministic, auditable
rule-set that governs how objects, people, institutions, and aggregates come into
existence, persist, transform, and are retired — without fabrication.

This spec is documentation-only. It introduces no runtime logic.

## Core axioms (locked)
1) Nothing exists unless it was constructed.
2) Construction consumes inputs and time.
3) Construction requires authority.
4) Destruction produces traceable outcomes.
5) Aggregation preserves provenance hashes.
6) Refinement recreates the same entities deterministically.
7) Ownership is never implicit.
8) Transfers are explicit events.
9) Death does not delete identity.
10) Provenance is required at all fidelity tiers.

## Definitions

### Provenance record
A deterministic record of origin. Contains:
- unique provenance_id
- creator (person/org)
- creation method (birth, build, issue, import)
- inputs consumed
- construction site
- time range (ACT start/end)
- authority under which it was created

### Construction
A process that transforms inputs into an entity. Always:
- scheduled
- resource-consuming
- time-consuming
- auditable

### Entity
Any persistent thing:
- person
- body
- structure
- vehicle
- organization
- instrument
- abstract aggregate

### Aggregate provenance
A summarized provenance for macro/meso entities. Must preserve:
- total counts
- total inputs
- contributing provenance hashes

Aggregate provenance NEVER invents new provenance.

### Destruction / retirement
Explicit state transitions. Outputs:
- debris
- salvage
- waste
- death records

Identity persists even if embodiment does not.

## Provenance across fidelity tiers

### Macro aggregates
Examples:
- population cohorts
- city inventories
- national treasuries

Rules:
- macro provenance is a hash set summary
- refinement maps macro provenance -> micro provenance deterministically
- collapse recomputes macro provenance without loss

### Meso entities
Examples:
- cities
- factories
- organizations

Rules:
- meso provenance retains contributing macro hashes and local construction events

### Micro entities
Examples:
- people
- machines
- buildings

Rules:
- micro provenance is explicit and directly auditable

## Births, deaths, and lineage (mandatory)

### Birth
Birth is a construction event:
- inputs: two parents + resources + time
- outputs: new person with lineage provenance

### Death
Death is a transition:
- body becomes dead
- person identity persists
- estate is created

### Lineage tracking
Track:
- parentage
- inheritance eligibility
- demographic aggregation

## Ownership and transfer (mandatory)
Ownership is a first-class relation. Transfers occur via:
- trade
- inheritance
- seizure
- abandonment

Transfers must:
- reference prior owner
- be authorized
- be auditable

No implicit ownership changes.

## Abstract and unreachable entities
Abstract aggregates are allowed only when unreachable in practice.
Abstract entities MUST:
- still have provenance
- still be auditable

Abstract entities MUST NOT:
- be refined unless reachability changes

## Engine vs game responsibilities

Engine (Domino, C89/C90) MAY:
- provide canonical ID generation
- provide hash utilities
- enforce invariants

Engine MUST NOT:
- manage construction queues
- interpret authority
- decide ownership

Game (Dominium, C++98) MUST:
- schedule construction
- manage provenance records
- enforce authority and governance
- integrate with economy and law
- expose inspection tools

## Ledger integration notes
- Ledger lots MUST carry provenance_id and source transaction metadata.
- Lot creation is deterministic and tied to transaction application time.
- Aggregate provenance hashes are derived from lot metadata and preserved across
  refinement/collapse.

## Integration points (mandatory)
- Fidelity Projection Engine (FP0)
- Economy & Ledger (E*)
- Command & Doctrine (CMD*)
- Time system (T*)
- Death & Continuity (LIFE*)
- World Source Stack (WSS*)

## Prohibitions (enforced)
- Auto-spawned background populations
- Regenerating cities
- Silent entity deletion
- "Magic" respawn
- Non-auditable aggregation
- Engine-side provenance shortcuts

## Worked scenarios (mandatory)

### Early-game village growth
Construction events create new dwellings and inhabitants. Aggregates update with
contributing provenance hashes. No implicit population generation.

### Late-game megacity aggregation
Micro entities collapse to macro aggregates; counts and inputs are conserved with
provenance hash summaries.

### Inheritance after death
Death creates an estate; ownership transfers are explicit and auditable.

### MMO shard transfer
Provenance records and hashes transfer with aggregate state, preserving identity.

## ASCII diagram

  [ Construction Inputs ] -> [ Construction Event ] -> [ Entity + Provenance ]
             |                                      |
             v                                      v
        [ Ledger ]                           [ Aggregate Provenance ]

## Test and validation requirements (spec-only)
Implementations must provide:
- provenance conservation tests
- refinement/collapse provenance tests
- birth/death lineage tests
- ownership transfer tests
- MMO consistency tests
