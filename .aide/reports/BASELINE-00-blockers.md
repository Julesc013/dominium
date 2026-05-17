# BASELINE-00 Blockers

Status: DERIVED
Last Reviewed: 2026-05-17

## Blocking Issues

None for the baseline freeze.

## Warning-Only Conditions

- Full promotion CTest was not run.
- Full eval was not run.
- No public release, GitHub release, tag, upload, installer, or package publication was created.
- Generated release/projection/build/local output remains ignored proof evidence and must not be committed.
- The release staging manifest records stager-time commit provenance that predates the BASELINE-00 freeze HEAD.

## Future Blocking Regressions

- Required tier command failure that is not already warning-only in the baseline.
- Internal pilot or portable projection validator failure when required by the move family risk class.
- Missing required release/projection manifest, proof report, checksum, provenance, or native binary without documented regeneration and validation.
- Any generated output staged or committed.
- Any unauthorized root move, delete, rename, alias, move map, salvage map, top-level root, or exception retirement.
- Any product, pack, profile, bundle, semantic contract, virtual-root, package, or release identity change outside explicit reviewed scope.
- Any worsening warning without written disposition.

## Follow-Up

```text
MOVE-FAMILY-00-PLAN - Governance, Meta, Performance, Validation, and IDE Cleanup Plan
```
