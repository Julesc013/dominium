Status: DERIVED
Last Reviewed: 2026-02-08
Supersedes: none
Superseded By: none

# Dist Tree Contract

## Scope

This document defines immutable layout intent for distribution outputs.
Canonical platform IDs and alias bans are defined in
`docs/distribution/PLATFORM_ID_CANON.md`.

## Tree Roles

- `dist/pkg/<platform>/<arch>/`: shipping package artifacts (`.dompkg`) and indexes.
- `dist/sys/<platform>/<arch>/`: realized install projection for local/CI use.
- `dist/sym/<platform>/<arch>/`: symbol artifacts; separate shipment channel.
- `dist/res/`: data resources used by packaging inputs.
- `dist/cfg/`: configuration templates used by setup/launcher.
- `dist/redist/`: runtime redistributables only.
- `dist/meta/`: build metadata, package indexes, and manifest exports.

## Shipping vs Produced

- Shipping primary artifact: `dist/pkg`.
- Produced operational tree: `dist/sys`.
- Symbols are never merged into runtime payload packages.

## Mutability

- Mutable by setup only: realized install state under `dist/sys` in CI/local flows.
- Immutable once produced: package bytes under `dist/pkg`, metadata under `dist/meta`.
- Launcher is read-only relative to install projections.

## Governance

- If `dist/sys` changes are published without corresponding package artifacts,
  governance must refuse release packaging.
- Platform directory names must be canonical (`winnt`, `macosx`, `linux`,
  `android`, `ios`, `web`, plus declared legacy IDs in registry).
