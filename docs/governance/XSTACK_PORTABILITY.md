Status: CANONICAL
Last Reviewed: 2026-02-14
Supersedes: none
Superseded By: none

# XStack Portability Guide

## Purpose

This guide documents how to transplant the XStack governance and gate execution model into another repository without restructuring Dominium.

## Minimal Required Components

- `scripts/dev/gate.py`
- `tools/xstack/core/`
  - `impact_graph.py`
  - `merkle_tree.py`
  - `cache_store.py`
  - `plan.py`
  - `scheduler.py`
  - `runners.py`
  - `runners_base.py`
- `data/registries/gate_policy.json`
- `data/registries/testx_groups.json`
- `data/registries/auditx_groups.json`
- `data/registries/xstack_components.json`
- `data/registries/derived_artifacts.json`

## Integration Entry Points

1. Implement runner adapters conforming to `tools/xstack/core/runners_base.py`.
2. Wire project-specific impact mappings in `testx_groups.json`, `auditx_groups.json`, and `xstack_components.json`.
3. Define profile semantics and escalation in `gate_policy.json`.
4. Add deterministic artifact contract metadata in `derived_artifacts.json`.

## Path Configuration

- The planner and impact graph assume repo-relative paths.
- Group path patterns are glob-based and should match top-level subsystem folders.
- Cache defaults to `.xstack_cache/`; this path should stay local and ignored by VCS.
- Structural scope declarations should stay registry/config driven (no absolute paths).

### Structural Scope Configuration

- Define scope roots per rule group (for example, `repox.structure.code` -> `engine|game|client|server`).
- Define artifact-class filters per scope (`CANONICAL` only for structural dep hashes).
- Define explicit non-canonical prefix exclusions per scope:
  - `docs/audit/`
  - `dist/`
  - `build/`
  - `tmp/`
  - `.xstack_cache/`

Use `docs/governance/XSTACK_SCOPE_TEMPLATE.json` as the portable baseline for new repos.

## Minimal vs Full Stack

- Minimal stack:
  - RepoX + TestX + AuditX grouped runners
  - FAST/STRICT profiles
  - Merkle + cache + deterministic plan
- Full stack:
  - PerformX + CompatX + SecureX adapters
  - FULL/FULL_ALL sharded execution
  - profiling and repo health snapshot artifacts

## Optional Components

- `tools/xstack/core/repo_health.py` snapshot generator
- throughput reports in `docs/audit/xstack/`
- FULL plan size warning artifact (`FULL_PLAN_TOO_LARGE.md`)

## Migration Notes

- Keep canonical artifact IDs stable when moving registries.
- Keep rule IDs stable when moving RepoX rulesets.
- Re-map command invocations, not governance semantics.
- Keep canonical roots and scope filters in data/config, not hardcoded absolute repo paths.
