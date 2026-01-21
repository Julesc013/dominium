# Life and Population (LIFE0+)

Status: binding.
Scope: canonical life model for individuals, populations, and agents.

This document defines what it means for beings to exist and scale from one
person to billions while preserving determinism, provenance, and auditability.

## Life entities
A Life Entity is something that can be born and can die. Types:
- INDIVIDUAL: micro, unique identity with embodiment.
- COHORT: macro aggregate with bounded membership.
- ABSTRACT_POPULATION: statistical population without individuals.
- SYNTHETIC_AGENT: non-biological actor, macro or micro.

All life entities have:
- life_id (stable)
- existence_state
- identity_state
- lineage_refs
- provenance_refs

## Population layers
1) MICRO: individuals and bodies.
2) MESO: groups, families, units.
3) MACRO: cohorts and statistics.

Macro populations may exist indefinitely without micro simulation. Micro
individuals are realized only when interacted with, observed, or required by
law/refinement.

## Anti-fabrication invariants (absolute)
- No life appears without birth.
- No life disappears without death.
- No population changes without explicit effects.
- No micro individuals fabricated from macro without a contract.

## Configuration, not modes
Hardcore, softcore, spectator, and reincarnation are data configurations:
abilities + authority + contracts. There are no game modes.

## Integration points
- Reality layer: `docs/arch/REALITY_LAYER.md`
- Existence states: `schema/existence/SPEC_EXISTENCE_STATES.md`
- Refinement contracts: `schema/existence/SPEC_REFINEMENT_CONTRACTS.md`
- Life entities: `schema/life/SPEC_LIFE_ENTITIES.md`
- Population models: `schema/life/SPEC_POPULATION_MODELS.md`

## See also
- `docs/arch/WHY_NPCS_DONT_POP.md`
- `docs/arch/IDENTITY_ACROSS_TIME.md`
- `docs/arch/DEATH_AND_CONTINUITY.md`
