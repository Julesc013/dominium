# Code/Data Boundary (CODEHYGIENE-X)

This document defines the permanent boundary between code and data. It is
binding for engine, game, tools, schemas, and CI enforcement.

## Goals
- Eliminate hardcoded taxonomies and magic numbers without performance loss.
- Keep deterministic execution, law gating, and Work/Access IR discipline.
- Preserve engine/game separation and schema authority.

## Categories (Binding)

### Category A — Architectural Enums (closed-world, code-owned)
Examples: ExistenceState, DeterminismClass, AuthorityLayer, ExecutionPhase.
Rules:
- Allowed in code; must be finite and closed-world.
- No CUSTOM/OTHER values.
- May change only via architecture process.

### Category B — Taxonomies of Reality (open-world, data-owned)
Examples: resources, materials, item types, damage types, biome tags,
capability IDs, law targets, module IDs, tech IDs.
Rules:
- Must NOT be represented as enums in runtime logic.
- Represented as stable IDs (u32) via registries.
- Strings resolve only at load/authoring time (never in hot paths).

### Category C — Tunable Parameters (data-owned, immutable at runtime)
Examples: thresholds, budgets, rates, curve params, caps.
Rules:
- Loaded once, validated, then treated as immutable constants.
- No magic numbers in authoritative code paths.

### Category D — Derived Conveniences (generated deterministically)
Examples: compiled lookup tables, packed views, baked SDF tiles, indices.
Rules:
- Generated deterministically from source data.
- Never authoritative unless explicitly declared.

## Enforcement
This boundary is enforced by:
- Hygiene scans and queue (docs/ci/HYGIENE_QUEUE.md).
- CI rules (docs/ci/CODEHYGIENE_RULES.md).
- Registry pattern (docs/architecture/REGISTRY_PATTERN.md).

## Workflow
1) Scan and classify violations.
2) Queue migrations with IDs and test coverage.
3) Apply safe migrations in batches; keep scope small.
4) Enforce via CI checks and update the queue.

## References
- docs/architecture/REGISTRY_PATTERN.md
- docs/ci/CODEHYGIENE_RULES.md
- docs/architecture/INVARIANTS.md
