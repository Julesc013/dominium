Status: CANONICAL
Last Reviewed: 2026-02-14
Supersedes: none
Superseded By: none

# XStack Track/Ignore Policy

## Purpose

This policy defines which XStack outputs are tracked in git, which outputs are ignored, and which command modes are allowed to write tracked audit artifacts.

## Artifact Classes

- `CANONICAL`: deterministic machine-readable outputs used for enforcement and longitudinal baselines.
- `DERIVED_VIEW`: deterministic human-facing renderings of canonical outputs.
- `RUN_META`: operational diagnostics (timings, host details, cache metadata) that are never used as gate inputs.

## Commit Policy

- `ALWAYS`: tracked and may be updated by explicit tool workflows.
- `SNAPSHOT_ONLY`: tracked but only updated by `gate.py snapshot`.
- `NEVER`: never tracked; must be emitted under cache/workspace roots.

The authoritative mapping is `data/registries/derived_artifacts.json`.

## Write Roots

- `docs_audit`: tracked audit documents and canonical snapshots.
- `workspace`: workspace-scoped generated outputs.
- `cache`: local ephemeral execution data.

## Command Write Behavior

- `gate.py verify|strict|full|doctor`
  - must not modify tracked files.
  - writes only under `.xstack_cache/` or workspace-scoped temp roots.
- `gate.py snapshot`
  - may update `SNAPSHOT_ONLY` artifacts in `docs/audit/`.
  - must preserve deterministic ordering and canonical JSON constraints.

## Ignored Paths

- `.xstack_cache/**`
- `dist/ws/**`
- `out/**`
- `build/**`
- `tmp/**`
- transient run logs (`*.log`, `*.trace`)

## Required Guardrails

- RepoX invariant `INV-NO-TRACKED-WRITES-DURING-GATE` enforces non-snapshot write discipline.
- RepoX invariant `INV-RUNTIME-NO-XSTACK-IMPORTS` prevents runtime coupling to XStack tooling.
- TestX gate write tests enforce read-only behavior for `verify`, `strict`, and `full`.

