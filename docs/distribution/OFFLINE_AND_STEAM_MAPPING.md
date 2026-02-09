Status: DERIVED
Last Reviewed: 2026-02-08
Supersedes: none
Superseded By: none

# Offline And Steam Mapping

## Scope

This document defines offline cache transport and Steam depot mapping for
package-based distribution.

## Offline Cache Workflow

1. Build package set into `dist/pkg/<platform>/<arch>/`.
2. `setup verify-cache` on source host.
3. `setup export-cache --dest <portable_path>`.
4. Transfer exported cache to target host.
5. `setup install --profile <profile_id> --from-cache <portable_path> --platform <p> --arch <a>`.

Rules:

- No network access is required for steps 3-5.
- Cache verification is mandatory before install.

## Steam Mapping

- Depot payloads map to package artifacts or chunk stores.
- Recommended mapping:
  - Core runtime depots: core package group ids.
  - Optional language/content depots: locale/content package group ids.
  - Symbols: separate non-player depot/channel.

## Determinism Constraints

- Same package set and same profile resolution must produce identical lockfiles.
- Install projection digest must match across online/offline modes.

## Refusal Codes

- `refuse.offline_cache_missing`
- `refuse.offline_cache_corrupt`
- `refuse.depot_mapping_missing_package`
