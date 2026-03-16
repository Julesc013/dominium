Status: CANONICAL
Last Reviewed: 2026-03-13
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: RESTRUCTURE
Replacement Target: release-pinned convergence and deprecation policy after layout cleanup

# Shim Policy

This document governs the temporary compatibility shims used during repository convergence.

## Rules

- Shims must be deterministic.
- Shims must emit a deprecation warning with explicit replacement instructions.
- Shims must be tagged provisional with a replacement target and sunset target.
- Shims must route through governed surfaces only:
  - virtual paths for path redirects
  - AppShell bootstrap for legacy flags
  - `dom <area> ...` for legacy tool replacement guidance
  - `validate --all` for legacy validation entrypoints

## Shims Must Never

- bypass pack verification
- bypass contract pin validation
- bypass capability negotiation
- become the primary or only supported runtime path

## Transitional Scope

- Path shims redirect common legacy relative roots such as `./packs`, `../packs`, and `./data`.
- Flag shims preserve legacy CLI affordances such as `--portable` and `--no-gui`.
- Tool shims keep selected direct tool entrypoints callable while pointing users to the stable `dom` umbrella.
- Validation shims keep legacy aggregate validation wrappers functional while routing them through the unified validation pipeline.
