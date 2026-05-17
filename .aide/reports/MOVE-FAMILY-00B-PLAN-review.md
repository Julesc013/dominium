# MOVE-FAMILY-00B-PLAN Review

Status: DRAFT
Last Reviewed: 2026-05-17
Approval Status: not_approved
Apply Allowed: false

## Review Summary

MOVE-FAMILY-00B-PLAN is ready for gate review. It plans a narrow source-metadata migration for the three tracked files under `ide/manifests/**` and leaves all physical work unauthorized.

## Manifests Found

- `ide/manifests/projection_manifest.schema.json`
- `ide/manifests/projection_manifest_examples/example_linux_clang_modern_client_gui.projection.json`
- `ide/manifests/projection_manifest_examples/example_win_vc6_win9x_client_gui.projection.json`

## Ownership Classification

All three files are classified as projection contract metadata. The examples are authored contract fixtures, not generated proof output.

## Proposed Target Paths

- `contracts/projections/ide/projection_manifest.schema.json`
- `contracts/projections/ide/examples/example_linux_clang_modern_client_gui.projection.json`
- `contracts/projections/ide/examples/example_win_vc6_win9x_client_gui.projection.json`

## Consumers And References

Apply-phase rewrites are planned for:

- `.gitignore`
- `scripts/verify_docs_sanity.py`
- `docs/architecture/REPO_OWNERSHIP_AND_PROJECTIONS.md`
- `docs/architecture/PROJECTION_LIFECYCLE.md`
- `docs/architecture/IDE_PROJECTIONS.md`

Review/no-rewrite posture is planned for generated output producers:

- `scripts/ide_gen.sh`
- `scripts/ide_gen.bat`
- `cmake/ide/IdeProjectionManifest.cmake`

Historical/generated evidence should not be rewritten.

## Rewrite Count

- Apply rewrite groups: 5.
- Review/later groups: 5.
- Historical never-rewrite groups: 4.

## Validation Plan

The later apply task must run Tier 0, focused RepoX, JSON/TOML parsing, manifest schema/example parse checks, strict repo/root/distribution/component validators, docs/build/UI/ABI checks, generated-output ignored/staging checks, and stale reference scans.

## Rollback Plan

Rollback is reverse moves, reverse reference rewrites, reverse exception update, optional removal of empty `contracts/projections/ide/**` directories, then Tier 0 validation.

## Exception Effect

If all three planned moves apply and `git ls-files ide` becomes empty, the `ide` source-layout exception can be retired after validation. Ignored generated `ide/**` output may still exist locally.

## Readiness

Ready for `MOVE-FAMILY-00B-GATE`: yes.

Apply remains unauthorized until a gate approves the exact scope.

## No Moves Confirmation

This task applied no moves, deletes, renames, reference rewrites, active aliases, compatibility shims, move maps, salvage maps, or exception updates.
