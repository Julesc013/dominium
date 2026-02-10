Status: CANONICAL
Last Reviewed: 2026-02-10
Supersedes: none
Superseded By: none

# Worldgen Pipeline

World generation is modular, deterministic, and data-driven.

## Pipeline Shape

1. Resolve enabled worldgen modules from registry and packs.
2. Build deterministic module DAG from declared dependencies.
3. Generate WorldGenPlan artifact.
4. Execute modules with named RNG streams.
5. Emit WorldSpec and preview layers.

## Module Contract

- Module declarations live in schema and registry data.
- Each module declares inputs, outputs, refusal codes, and preview layers.
- Unknown modules are refused explicitly.

## Determinism Rules

- Stable module ordering and tie-break rules.
- Named RNG stream derivation by plan identity and module ID.
- Deterministic refusal paths for missing dependencies.

