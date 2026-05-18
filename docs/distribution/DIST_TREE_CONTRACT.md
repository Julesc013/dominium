Status: DERIVED
Last Reviewed: 2026-02-08
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Dist Tree Contract

## CONVERGE-04 Projection Note

This document remains an input/partial contract for generated `archive/generated/dist/` output roles. CONVERGE-04 reconciles distribution, install, media, package, bundle, cache, staging, symbols, and runtime projection layout at `contracts/distribution/layout.contract.toml` and `docs/repo/DISTRIBUTION_LAYOUT_CANON.md`.

## Scope

This document defines immutable layout intent for distribution outputs.
Canonical platform IDs and alias bans are defined in
`docs/distribution/PLATFORM_ID_CANON.md`.

## Tree Roles

- `archive/generated/dist/pkg/<platform>/<arch>/`: shipping package artifacts (`.dompkg`) and indexes.
- `archive/generated/dist/sys/<platform>/<arch>/`: realized install projection for local/CI use.
- `archive/generated/dist/sym/<platform>/<arch>/`: symbol artifacts; separate shipment channel.
- `archive/generated/dist/res/`: data resources used by packaging inputs.
- `archive/generated/dist/cfg/`: configuration templates used by setup/launcher.
- `archive/generated/dist/rearchive/generated/dist/`: runtime redistributables only.
- `archive/generated/dist/meta/`: build metadata, package indexes, and manifest exports.

## Shipping vs Produced

- Shipping primary artifact: `archive/generated/dist/pkg`.
- Produced operational tree: `archive/generated/dist/sys`.
- Symbols are never merged into runtime payload packages.

## Mutability

- Mutable by setup only: realized install state under `archive/generated/dist/sys` in CI/local flows.
- Immutable once produced: package bytes under `archive/generated/dist/pkg`, metadata under `archive/generated/dist/meta`.
- Launcher is read-only relative to install projections.

## Governance

- If `archive/generated/dist/sys` changes are published without corresponding package artifacts,
  governance must refuse release packaging.
- Platform directory names must be canonical (`winnt`, `macosx`, `linux`,
  `android`, `ios`, `web`, plus declared legacy IDs in registry).
