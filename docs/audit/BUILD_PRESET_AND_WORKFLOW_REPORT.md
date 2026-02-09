Status: DERIVED
Last Reviewed: 2026-02-09
Supersedes: none
Superseded By: none

# Build Preset And Workflow Report

## Scope

- This report records the build-lane, preset, and target contract now enforced for host IDE build flows.
- It covers lane mapping, verification targets, release gate behavior, and smoke-runner integration.

## Canonical lane mapping

- DEV lane defaults:
  - configure preset `msvc-dev-debug` on Windows
  - build target `all_runtime`
  - verification target `verify_fast`
- VERIFY lane:
  - `verify_fast` for bounded checks
  - `verify_full` for full TestX (`testx_all`)
- RELEASE lane:
  - explicit release presets (`release-winnt-x86_64`, `release-linux-x86_64`, `release-macos-arm64`)
  - packaging via `dist_all` only
  - guarded by `dom_dist_release_lane_guard`

## Enforced targets

- Runtime umbrellas:
  - `all_libs`
  - `all_apps`
  - `all_tools`
  - `all_renderers`
  - `all_runtime`
- Verification:
  - `verify_fast`
  - `verify_full`
- Distribution:
  - `dist_pack`
  - `dist_index`
  - `dist_verify`
  - `dist_smoke`
  - `dist_all`

## Guard behavior

- `dist_*` targets require release lane (`DOM_BUILD_KIND` in `release|beta|rc|hotfix`).
- `dist_*` targets require non-empty `DOM_BUILD_GBN` that is not `none`.
- `testx_all` does not hard-depend on packaging targets.

## Smoke runner

- Bounded smoke runner script: `tools/ci/smoke_run_apps.py`.
- Runs from random temporary CWD.
- Probes:
  - `setup`, `launcher`, `client`, `server`
  - mode refusal behavior for launcher TUI/GUI probes
  - UI tool surfaces (`tool_ui_bind`, `tool_ui_validate`, `tool_ui_doc_annotate`)
- Output JSON (when invoked via CMake target):
  - `out/build/<preset>/smoke_run_apps.json`

## RepoX/TestX integration

- RepoX enforces preset/target contract: `INV-BUILD-PRESET-CONTRACT`.
- RepoX enforces release-lane packaging guard: `INV-DIST-RELEASE-LANE-GATE`.
- TestX build matrix checks preset/target contract:
  - `tests/ops/build_matrix_tests.py`.

## Validation snapshot

- RepoX: pass (`python scripts/ci/check_repox_rules.py --repo-root .`)
- Strict build: pass (`cmake --build out/build/vs2026/verify --config Debug --target domino_engine dominium_game`)
- Full TestX: pass (`cmake --build out/build/vs2026/verify --config Debug --target testx_all`)
- UI bind freshness: pass (`dist/sys/winnt/x64/bin/tools/tool_ui_bind.exe --repo-root . --check`)
