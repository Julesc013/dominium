Status: DERIVED
Last Reviewed: 2026-05-17
Supersedes: none
Superseded By: none

# MOVE-FAMILY-00B IDE Root Retirement Proof

## Status

- Task: `MOVE-FAMILY-00B-PROOF`
- Result: PASS_WITH_WARNINGS
- Baseline: BASELINE-00 / RELEASE-00 structural regression baseline
- Apply commit proven: `7077e317c3c87a75036c8b76fe70cce112ef0bbc`

## Scope

This proof verifies the previously applied IDE manifest migration. It does not move files, delete files, rename files, rewrite references, create shims, apply move maps, apply salvage maps, retire additional exceptions, or change product/runtime/source behavior.

## Root Retirement Result

- `git ls-files ide`: empty.
- Filesystem `ide/`: absent.
- Dirty status under `ide/`: none.
- `ide_root` exception: retired in `contracts/repo/layout_exceptions.toml`.

## Moved Files

| Replacement Path | Status |
| --- | --- |
| `contracts/projections/ide/projection_manifest.schema.json` | tracked, present, JSON parse PASS |
| `contracts/projections/ide/examples/example_linux_clang_modern_client_gui.projection.json` | tracked, present, JSON parse PASS |
| `contracts/projections/ide/examples/example_win_vc6_win9x_client_gui.projection.json` | tracked, present, JSON parse PASS |

## New Contract/Projection Home

The tracked schema and examples now live under `contracts/projections/ide/**`. Generated projection manifests may still be emitted under ignored local `ide/manifests/*.projection.json` paths by existing generation tooling; that is generated output, not tracked source authority.

## Exception Status

The `ide` source-layout exception is inactive under `[retired_exceptions.ide_root]`. Strict repo layout and root allowlist validators pass with the exception retired.

## Stale Reference Classification

Remaining old-path references are warning-only:

- root-recycling history;
- AIDE plan/report/context/generated evidence;
- planning and audit evidence;
- generated-output producer references for ignored local projection output;
- architecture docs that intentionally describe generated output paths.

No active source/tool/validator/current-doc blocker remains for the retired schema/example source paths.

## Baseline Validation

Validation passed with warnings:

- AIDE doctor/validate/test/selftest/tools/roots/repo/latest commit checks: PASS.
- Strict repo/root/distribution/component validators: PASS_WITH_WARNINGS due to known TOML fallback-parser warnings.
- Docs sanity, build target boundaries, UI shell purity, ABI boundaries: PASS.
- Focused RepoX: PASS through `ctest --preset verify -R inv_repox_rules --output-on-failure`.
- Manifest JSON parsing and required-field checks: PASS.
- Generated `.dominium.local/**` and `.aide.local/**` outputs remain ignored/untracked.

Full CTest, full eval, CMake configure/build, product binaries, package/release generation, portable projection regeneration, and internal pilot release regeneration were not run by proof scope.

## Remaining Warnings

- Historical/audit/planning/AIDE references to old IDE paths remain by design.
- Generated-output references to `ide/manifests/*.projection.json` remain by design.
- Known TOML fallback-parser warnings remain accepted warning-only output from strict validators.

## Next Task

```text
MOVE-FAMILY-00C-PLAN - Active Validation/Meta/Governance Tool Namespace Plan
```
