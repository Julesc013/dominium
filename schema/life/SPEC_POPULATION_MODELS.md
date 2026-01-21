--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- Deterministic scheduling primitives and refinement hooks.
GAME:
- Population rules, cohort logic, and macro/micro transitions.
SCHEMA:
- Population layer records and validation constraints.
TOOLS:
- Inspectors/editors only (no runtime behavior).
FORBIDDEN:
- No runtime logic in schema specs.
- No global scans over all populations.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SPEC_POPULATION_MODELS — Population Layers Canon

Status: draft
Version: 1

## Purpose
Define the canonical population representations used to scale life from one
person to billions while preserving determinism and continuity.

## Population layers (mandatory)
1) MICRO
   - Individual persons and bodies.
2) MESO
   - Groups, families, units, or bounded cohorts.
3) MACRO
   - Cohorts and statistical aggregates.

Macro populations may exist indefinitely without micro simulation.

## Refinement and collapse rules
- Micro individuals are realized only when:
  - interacted with,
  - observed,
  - required by law or refinement contract.
- Collapse aggregates micro -> macro deterministically.
- No micro individuals may be fabricated from macro without a refinement contract.
- Collapses must preserve conservation, lineage, and provenance summaries.

## Cohorts (macro aggregates)
Required fields (conceptual):
- cohort_id
- life_id (cohort Life Entity)
- population_count
- demographic_summary_ref
- lineage_summary_ref
- provenance_ref
- existence_state

## ABSTRACT_POPULATION (statistical)
Required fields (conceptual):
- population_id
- life_id (abstract Life Entity)
- statistical_model_ref
- population_count
- provenance_ref
- existence_state

## Determinism and budgets
- Transitions are scheduled events; no per-tick global updates.
- Selection of micro subjects is deterministic and bounded by interest sets.
- Budgets may defer refinement, but must not fabricate placeholders.

## Integration points
- Refinement contracts: `schema/existence/SPEC_REFINEMENT_CONTRACTS.md`
- Reality layer: `docs/arch/REALITY_LAYER.md`
- Visitability: `docs/arch/VISITABILITY_AND_REFINEMENT.md`

## See also
- `schema/life/SPEC_LIFE_ENTITIES.md`
