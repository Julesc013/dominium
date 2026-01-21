--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- Stable IDs, hashing, deterministic scheduling primitives.
GAME:
- LIFE semantics, identity rules, birth/death orchestration.
SCHEMA:
- Canonical LIFE entity records and validation constraints.
TOOLS:
- Inspectors/editors only (no runtime behavior).
FORBIDDEN:
- No runtime logic in schema specs.
- No implicit life fabrication.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SPEC_LIFE_ENTITIES — Life Entity Canon

Status: draft
Version: 1

## Purpose
Define the canonical LIFE entity model used by all biological individuals,
macro populations, AI agents, and player characters. This spec defines data
formats and invariants only; no runtime logic is introduced.

## Life Entity (canonical)
A Life Entity represents something that can be born and can die.

Types:
- INDIVIDUAL (micro, unique person with embodiment)
- COHORT (macro aggregate with bounded membership)
- ABSTRACT_POPULATION (statistical population without individuals)
- SYNTHETIC_AGENT (non-biological actor, may be macro or micro)

## Required fields (all Life Entities)
- life_id (stable, unique within a timeline)
- life_type (INDIVIDUAL | COHORT | ABSTRACT_POPULATION | SYNTHETIC_AGENT)
- existence_state (EXIST0 state)
- identity_state (see below)
- lineage_refs (parent/ancestor links and certainty)
- provenance_refs (origin and causal chain)

### identity_state (canonical)
Identity state tracks continuity, not life status:
- ACTIVE (identity is current in this timeline)
- ARCHIVED (identity preserved in archival history)
- FORKED (identity is a child of a forked lineage root)

Death does not change identity_state; it changes life state for INDIVIDUAL
entities (e.g., alive_state in the embodiment record).

## INDIVIDUAL (micro)
An INDIVIDUAL is represented by:
- identity record (person)
- optional embodiment record (body/instance)

The identity record is persistent across refinement and collapse. The embodiment
may appear/disappear with refinement, but never alone defines identity.

## COHORT and ABSTRACT_POPULATION (macro)
- COHORT: bounded aggregate with membership constraints.
- ABSTRACT_POPULATION: statistical mass without individual identity.

Macro entities may exist indefinitely without micro simulation.

## SYNTHETIC_AGENT
Synthetic agents follow the same birth/death contracts but may be defined
without biological constraints. They may exist as macro planners and refine
to individuals when required.

## Invariants (absolute)
- No life entity appears without a BirthContract effect.
- No life entity disappears without a DeathContract effect.
- No micro individuals are fabricated from macro without a refinement contract.
- identity_state must not be deleted; it may be archived or forked only.

## Integration points
- Existence states: `schema/existence/SPEC_EXISTENCE_STATES.md`
- Refinement contracts: `schema/existence/SPEC_REFINEMENT_CONTRACTS.md`
- Reality layer: `docs/arch/REALITY_LAYER.md`

## See also
- `schema/life/SPEC_POPULATION_MODELS.md`
- `schema/life/SPEC_IDENTITY_AND_LINEAGE.md`
