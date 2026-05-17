Status: DERIVED
Last Reviewed: 2026-05-17
Supersedes: none
Superseded By: none

# MOVE-FAMILY-00B-PROOF Blockers

## Blocking Issues

None.

## Non-Blocking Warnings

- Historical, planning, audit, root-recycling, and AIDE evidence references to old `ide/manifests/**` paths remain by design.
- Generated-output producer references to `ide/manifests/*.projection.json` remain by design for ignored local IDE projection output.
- Strict validators passed while emitting known TOML fallback-parser warnings.
- Full CTest, full eval, CMake configure/build, product binary execution, package/release generation, portable projection regeneration, and internal pilot release regeneration were not run by proof scope.

## Authorization Status

- Move apply authorized: false.
- Feature work authorized: false.
- Additional layout exception retirement authorized: false.
- Recommended next task: `MOVE-FAMILY-00C-PLAN - Active Validation/Meta/Governance Tool Namespace Plan`.
