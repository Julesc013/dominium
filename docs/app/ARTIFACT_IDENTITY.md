Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Artifact Identity

This document defines build/version identity fields for all products.

## Build metadata sources
- Global build number: `.dominium_build_number`
- Generated version header: `dominium/build_version.generated.h`
- Generated config header: `domino/config_base.h`

## Required identity fields (printed by `--build-info`)
- `product` and `product_version`
- `engine_version` and `game_version`
- `build_number`
- `build_id`, `git_hash`, `toolchain_id`
- Protocol versions:
  - `protocol_law_targets`
  - `protocol_control_caps`
  - `protocol_authority_tokens`
- API/ABI versions:
  - `abi_dom_build_info`
  - `abi_dom_caps`
  - `api_dsys`
  - `api_dgfx`

## Renderer identity
- When multiple renderer backends are compiled into a single binary, the
  renderer identity may be reported as `multi` in higher-level metadata.
- Explicit renderer selection must fail loudly if the backend is unavailable.

## Mismatch behavior
- Protocol or ABI mismatches are treated as hard errors in app-layer checks.
- No silent fallback is permitted when an explicit renderer is requested.