Status: DERIVED
Last Reviewed: 2026-02-14
Supersedes: none
Superseded By: none

# RepoX Scope Analysis (Cold Path)

## Baseline Evidence

- Source: `docs/audit/xstack/PROFILE_BASELINE.json`
- Source: `docs/audit/repox/REPOX_PROFILE.json`
- Observed dominant phase: `repox.core.structure`
  - `823676 ms` in RepoX profile
  - `~93.2%` of `total_duration_ms=883658`

## Current Structural Dependency Roots

`repox.core.structure` currently keys cache/input hash from:

- `repo`
- `scripts`
- `tests`

The group currently executes these checks:

- top-level/layout and archive checks
- frozen-contract surface checks
- authoritative symbol and tool path checks
- gate-calling and remediation metadata checks
- failure class and identity fingerprint checks

## Invalidation Triggers Seen in Baseline

Changed-path set in the captured run includes both:

- governance/runtime code and registry edits (`scripts/ci/*`, `repo/repox/*`, `schema/*`, `data/registries/*`)
- run-meta/derived outputs under `docs/audit/*`

Because the structural group is monolithic, a miss in that one group forces full re-evaluation of all checks in the group.

## Why Run-Meta Can Still Disturb Cold-Path Behavior

Even when a run-meta file is not itself authoritative, cold-path invalidation can still occur when:

- hashing is subtree-wide without artifact-class filtering per group, and/or
- a mixed group combines checks with different real scopes, so any dependent subtree change reruns all checks.

The fix is to split structural checks into scoped groups and compute input hashes with artifact-aware filtering (canonical-only where required).
