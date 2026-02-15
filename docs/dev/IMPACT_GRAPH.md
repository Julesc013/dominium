Status: DERIVED
Version: 1.0.0
Last Reviewed: 2026-02-15
Compatibility: `tools/dev/impact_graph/` and `tools/xstack/testx/runner.py`.

# Impact Graph

## Purpose

The deterministic impact graph converts source-tree changes into reproducible impacted sets used for:

- FAST TestX subset selection
- impacted build target reporting
- CI acceleration diagnostics

Binding references:

- `AGENTS.md`
- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `docs/dev/DEVELOPER_ACCELERATION_MODEL.md`

## Node types

- `file`: repository file path node
- `schema`: canonical schema node under `schemas/`
- `registry`: registry/data contract node
- `pack`: pack manifest identity node
- `product`: build/runtime product node (`engine`, `game`, `client`, `server`, `launcher`, `setup`, `tools`)
- `test`: TestX test node (`tools/xstack/testx/tests/test_*.py`)
- `artifact`: derived artifact node (e.g. `build/lockfile.json`, `build/registries/*.json`)
- `domain`: domain registry identity node
- `solver`: solver registry identity node
- `command`: deterministic command surface node (dev/xstack command IDs)

## Edge types

- `depends_on`: generic dependency edge
- `includes`: include/import dependency edge
- `references`: textual/structural reference edge
- `validates`: validator/test to target edge
- `generates`: producer to artifact edge
- `enforces`: policy/invariant to target edge

Edge direction convention:

- `A -> B` means A depends on/references/validates/enforces/generates B, depending on edge type.

## Deterministic graph construction

Construction invariants:

- stable path normalization to `/`
- stable sorted node and edge ordering
- ignore non-authoritative directories:
  - `build/`
  - `out/`
  - `dist/`
  - `tmp/`
  - `.vs/`
- canonical JSON output with sorted keys and newline-normalized text assumptions

Output artifact:

- `build/impact_graph.json`

This file is derived and may be regenerated at any time from repository content.

## Change propagation

Input:

- changed file set from deterministic VCS query

Propagation:

1. map changed files to `file:` nodes
2. traverse reverse dependency edges to collect impacted dependents
3. derive impacted subsets:
   - tests (`node_type=test`)
   - build targets/products (`node_type=product`)
   - affected artifacts (`node_type=artifact`)

If graph coverage is incomplete:

- acceleration layer must fall back to safe full-suite behavior
- no silent skip is permitted

## TestX subset computation

FAST subset computation:

1. build/refresh impact graph
2. compute impacted tests from changed files
3. if subset is valid and non-empty, run subset
4. else run full suite with explicit fallback reason in run metadata

STRICT/FULL:

- run full suite regardless of impact graph
- impact graph remains informative but non-authoritative for strict completeness

## Refusal behavior

Changed-only graph operations require VCS availability:

- refusal code: `refusal.git_unavailable`
- remediation: run full suite or execute on a Git-aware checkout

This refusal is deterministic and does not mutate runtime state.
