Status: DERIVED
Last Reviewed: 2026-05-17
Supersedes: none
Superseded By: none

# MOVE-FAMILY-00B-PROOF Status

## Status

- Task ID: `MOVE-FAMILY-00B-PROOF`
- Result: PASS_WITH_WARNINGS
- Branch: `main`
- HEAD at proof start: `7077e317c3c87a75036c8b76fe70cce112ef0bbc`
- origin/main at proof start: `7077e317c3c87a75036c8b76fe70cce112ef0bbc`
- Baseline protected: BASELINE-00 / RELEASE-00 structural regression baseline

## Root Retirement Summary

- `git ls-files ide`: empty.
- Filesystem `ide/` path: absent.
- Dirty status under `ide/`: none.
- `contracts/repo/layout_exceptions.toml`: `retired_exceptions.ide_root` is present and inactive.
- No additional layout exception was retired by this proof task.

## Moved File Verification

Tracked replacement files:

- `contracts/projection/ide/projection_manifest.schema.json`
- `contracts/projection/ide/examples/example_linux_clang_modern_client_gui.projection.json`
- `contracts/projection/ide/examples/example_win_vc6_win9x_client_gui.projection.json`

All three files exist, are tracked, parse as JSON, and remain non-empty. The schema remains schema-like with `$schema`, `type`, `properties`, and `required` keys. Both examples include all fields required by the schema.

## Exception State

The `ide` source-layout exception is retired, not active. Strict repo layout and root allowlist validators accept the retired exception state.

## Reference Classification

No active source, tool, validator, or current architecture reference remains to the retired schema/example source paths:

- `ide/manifests/projection_manifest.schema.json`
- `ide/manifests/projection_manifest_examples/example_linux_clang_modern_client_gui.projection.json`
- `ide/manifests/projection_manifest_examples/example_win_vc6_win9x_client_gui.projection.json`

Remaining old-path references are warning-only historical, planning, audit, AIDE evidence, root-recycling history, or generated-output producer references.

## Baseline Validation

Tier 0 and MOVE-FAMILY-00B proof validation passed. Focused RepoX passed. Full CTest, full eval, CMake configure/build, product binaries, package/release generation, portable projection regeneration, and internal pilot release regeneration were not run by proof scope.

## Next Recommendation

```text
MOVE-FAMILY-00C-PLAN - Active Validation/Meta/Governance Tool Namespace Plan
```

This continues family 00 by planning the active module/tooling surfaces that remain after `ide/` retirement. No apply is authorized by this proof.
