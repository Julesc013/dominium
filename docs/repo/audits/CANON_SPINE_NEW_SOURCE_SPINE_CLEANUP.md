Status: DERIVED
Last Reviewed: 2026-05-20
Supersedes: none
Superseded By: none

Status: PASS_WITH_WARNINGS

# CANON-SPINE-NEW Source Spine Cleanup

CANON-SPINE-NEW is the post-router cleanup that collapses second-level wrapper, duplicate, and generated-root contamination into the canonical source spine.

## Scope

- Collapse shell/app/appshell/appcore into `runtime/shell/`.
- Thin product app roots and keep shared runtime ownership under `runtime/`.
- Move user-facing editors/viewers into `apps/workbench/module/`.
- Move engine platform/render/store/import/export/install/test material to runtime/tools/release/tests owners.
- Prefer singular contract category roots and `game/domain/` for code ownership.
- Collapse `content/data` and `content/domain-data` into specific content/archive owners.
- Keep generated/local roots untracked.

## Validation Summary

- AIDE doctor/validate/test/selftest/tools/roots/repo: PASS.
- Strict repo/root/distribution/component validators: PASS.
- Bad-root absence: PASS, 0 tracked files under configured former bad roots.
- Smoke CTest: PASS.
- CMake configure: PASS.
- UI shell purity and ABI boundaries: PASS.
- Build target boundaries: FAIL_WITH_KNOWN_WARNINGS.
- Full verify CTest: NOT_GREEN.

## Follow-Up

Feature work remains blocked. The next task should repair the remaining boundary imports and drive full proof.
