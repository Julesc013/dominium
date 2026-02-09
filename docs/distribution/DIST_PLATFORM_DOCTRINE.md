Status: DERIVED
Last Reviewed: 2026-02-09
Supersedes: none
Superseded By: none

# Dist Platform Doctrine

## Scope

This document defines platform directory doctrine for `dist/*`.

## Dist Roots

- `dist/pkg/<platform>/<arch>/`: canonical shipping artifacts.
- `dist/meta/<platform>/<arch>/`: build metadata and package indexes.
- `dist/sym/<platform>/<arch>/`: symbols and debug artifacts.
- `dist/sys/<platform>/<arch>/`: realized install output only.

## Dist Sys Doctrine

- `dist/sys` is produced output, not a shipping source of truth.
- Setup writes/installs realized layouts into `dist/sys` (or install root).
- Packaging ships from `dist/pkg`.
- Launcher reads lockfiles and resolved instance config; it does not mutate
  installs.

## Canonical Platform Directory Names

Platform directory segments under `dist/pkg`, `dist/meta`, `dist/sym`, and
`dist/sys` must use canonical IDs from
`data/registries/platform_registry.json`.

Forbidden aliases (`win`, `windows`, `mac`, `osx`) are not allowed in those
paths.

## Derived/Mutable Contract

- Mutable via setup/CI projection: `dist/sys`.
- Immutable once produced for release evidence:
  - `dist/pkg`
  - `dist/meta`
  - `dist/sym`
