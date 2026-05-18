Status: DERIVED
Last Reviewed: 2026-02-09
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Dist Platform Doctrine

## Scope

This document defines platform directory doctrine for `archive/generated/dist/*`.

## Dist Roots

- `archive/generated/dist/pkg/<platform>/<arch>/`: canonical shipping artifacts.
- `archive/generated/dist/meta/<platform>/<arch>/`: build metadata and package indexes.
- `archive/generated/dist/sym/<platform>/<arch>/`: symbols and debug artifacts.
- `archive/generated/dist/sys/<platform>/<arch>/`: realized install output only.

## Dist Sys Doctrine

- `archive/generated/dist/sys` is produced output, not a shipping source of truth.
- Setup writes/installs realized layouts into `archive/generated/dist/sys` (or install root).
- Packaging ships from `archive/generated/dist/pkg`.
- Launcher reads lockfiles and resolved instance config; it does not mutate
  installs.

## Canonical Platform Directory Names

Platform directory segments under `archive/generated/dist/pkg`, `archive/generated/dist/meta`, `archive/generated/dist/sym`, and
`archive/generated/dist/sys` must use canonical IDs from
`contracts/registry/platform_registry.json`.

Forbidden aliases (`win`, `windows`, `mac`, `osx`) are not allowed in those
paths.

## Derived/Mutable Contract

- Mutable via setup/CI projection: `archive/generated/dist/sys`.
- Immutable once produced for release evidence:
  - `archive/generated/dist/pkg`
  - `archive/generated/dist/meta`
  - `archive/generated/dist/sym`
