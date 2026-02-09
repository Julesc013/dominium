Status: DERIVED
Last Reviewed: 2026-02-09
Supersedes: none
Superseded By: none

# SDK Readiness

## Scope

Validation of SDK product graph declarations, distribution profiles, and compile/link smoke coverage.

## Implemented

- `data/registries/product_graph.json` updated:
  - `dominium.product.sdk.engine` provides:
    - `export:sdk.engine`
    - `export:lib.engine`
    - `export:headers.engine`
    - `export:schemas.engine`
    - capability `capability.sdk.engine`
  - `dominium.product.sdk.game` provides:
    - `export:sdk.game`
    - `export:lib.game`
    - `export:headers.game`
    - `export:schemas.game`
    - capability `capability.sdk.game`
  - `sdk.game` requires `export:sdk.engine` and `export:lib.game`.
- Distribution profiles added:
  - `data/profiles/profile.sdk_engine.json`
  - `data/profiles/profile.sdk_game.json`
- Packaging group support added:
  - `tools/distribution/pkg_pack_all.py` groups `sdk-engine` and `sdk-game`.

## Test Coverage

- `tests/distribution/distribution_sdk_profile_tests.py`
  - validates graph exports/dependencies and profile package refs.
- Compile/link smoke tests:
  - `tests/distribution/sdk_engine_compile_smoke.c`
  - `tests/distribution/sdk_game_compile_smoke.cpp`
  - wired in `tests/distribution/CMakeLists.txt`.

## Readiness Statement

- SDK graph declarations: ready.
- SDK profile declarations: ready.
- SDK compile/link contract: verified by TestX smoke targets.
