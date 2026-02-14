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

## Required Schemas and Registries

Required schema surfaces:

- `schema/governance/derived_artifact_contract.schema`
- `schema/governance/xstack_components.schema`

Required registry surfaces:

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

## Tracked vs Ignored Outputs

- Tracked outputs are limited to canonical snapshot artifacts under `docs/audit/`.
- Normal gate commands (`verify|strict|full|doctor`) are read-only for tracked files.
- Run-meta outputs are written under:
  - `.xstack_cache/`
  - `dist/ws/<WS_ID>/tmp/`
  - build/workspace temporary roots
- Authoritative contract:
  - `docs/governance/XSTACK_TRACK_IGNORE_POLICY.md`
  - `data/registries/derived_artifacts.json`

## Runtime Decoupling Contract

- Runtime product trees (`engine/`, `game/`, `client/`, `server/`) must not import or include `tools/xstack`.
- Runtime CMake roots must not add `tools/xstack` include or source paths.
- Removability proof is enforced by:
  - RepoX invariant `INV-RUNTIME-NO-XSTACK-IMPORTS`
  - TestX integration test `test_xstack_removal_builds_runtime`

## Snapshot Contract

- `gate.py snapshot` is the only gate command that may update `SNAPSHOT_ONLY` tracked artifacts.
- Snapshot outputs must preserve deterministic ordering and avoid run-meta payload fields.
- `verify|strict|full|doctor` always route runner outputs to cache/workspace roots.

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

## Portability Validation Checklist

After transplanting XStack into a new repo:

1. Run `python scripts/dev/gate.py verify` and confirm tracked working tree stays clean.
2. Run `python scripts/dev/gate.py strict` to validate scoped rule and group execution.
3. Run `python scripts/dev/gate.py snapshot` and confirm only snapshot-designated artifacts changed.
4. Run RepoX and TestX rules for:
   - `INV-RUNTIME-NO-XSTACK-IMPORTS`
   - `INV-NO-TRACKED-WRITES-DURING-GATE`
   - `test_xstack_removal_builds_runtime`
