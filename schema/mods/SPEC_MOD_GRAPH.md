--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- Provides deterministic IDs and hashing primitives.
GAME:
- Resolves mod graphs, ordering, and identity hashing.
SCHEMA:
- Defines graph fields, refusal codes, and identity inputs.
TOOLS:
- Visualize graphs and explain refusals.
FORBIDDEN:
- No runtime logic in schema specs.
- No silent dependency resolution.
DEPENDENCIES:
- Engine -> none outside engine.
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> engine/game public APIs + schema.
--------------------------------
# SPEC_MOD_GRAPH - Deterministic Mod Graph Resolution (MOD0)

Status: draft  
Version: 1

## Purpose
Define deterministic mod dependency resolution and graph identity rules.

## Graph resolution rules
- Order is deterministic and stable:
  - Sort by `mod_id`.
  - Resolve dependencies via stable topological ordering.
- Refuse on:
  - Missing dependency.
  - Dependency version mismatch.
  - Conflicts.
  - Cycles.

## Identity hashing
Graph identity is computed from:
- Ordered mod list (`mod_id`, `mod_version`, `payload_hash`, `sim_affecting`)
- Active schema versions
- Active feature epochs

Hashing is deterministic and stable across runs.

## Instance binding
Instance manifests must record:
- Ordered mod list (as resolved)
- Payload hashes
- Schema versions
- Feature epochs
- Graph identity hash

## Refusal codes
- `MISSING_DEPENDENCY`
- `DEPENDENCY_VERSION_MISMATCH`
- `CONFLICT`
- `DUPLICATE_MOD`
- `CYCLE`

## Prohibitions
- No silent conflict resolution.
- No auto-reordering that changes with insertion order.

## Test plan (spec-level)
- Deterministic ordering under permuted inputs.
- Refusal on missing dependencies.
- Refusal on conflicts.
- Stable identity hash across runs.
