Status: CANONICAL
Last Reviewed: 2026-02-10
Supersedes: none
Superseded By: none

# Worldgen Pipeline

World generation is modular, deterministic, and data-driven.

## Pipeline Shape

1. Resolve enabled worldgen modules from registry and packs.
2. Build deterministic module DAG from declared dependencies.
3. Generate base WorldGenPlan artifact.
4. Resolve constraints (`stage.resolve_constraints`) when a constraints artifact is selected.
5. Compile world artifacts (`stage.compile_world_artifacts`) using selected seed.
6. Execute modules with named RNG streams.
7. Emit WorldSpec and preview layers.

## Constraint Stage

- Constraint stage is data-driven and deterministic.
- Constraints may be selected from pack-contributed registry entries (`worldgen_constraints` contributions).
- Selected IDs must resolve through compiled registry `build/registries/worldgen_constraints.registry.json`.
- Hard constraints are applied before soft-score ranking.
- Multi-seed expansion and tie breaks must be deterministic and auditable.
- Refusal codes:
  - `refusal.constraints_unsatisfiable`
  - `refusal.search_exhausted`
- When no constraints are selected, the pipeline uses base seed only and skips search expansion.

## Module Contract

- Module declarations live in schema and registry data.
- Each module declares inputs, outputs, refusal codes, and preview layers.
- Unknown modules are refused explicitly.

## Determinism Rules

- Stable module ordering and tie-break rules.
- Named RNG stream derivation by plan identity and module ID.
- Deterministic refusal paths for missing dependencies.
