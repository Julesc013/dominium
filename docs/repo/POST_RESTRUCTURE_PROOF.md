Status: DERIVED
Last Reviewed: 2026-05-18
Supersedes: none
Superseded By: none

# Post-Restructure Proof

## Latest Status

POST-RESTRUCTURE-00 is blocked before full proof execution.

## Current Blockers

- MOVE-BULK-08 did not authorize full proof.
- 1764 tracked files remain under formerly bad roots.
- Batches B-G remain deferred and Batch H remains blocked.
- Batch A still has 283 skipped files.

## Commands To Rerun After Remediation

- AIDE doctor/validate/test/selftest/tools/roots/repo/commit check.
- Strict repo/root/distribution/component validators.
- Focused RepoX.
- `cmake --preset verify` and `cmake --build --preset verify`.
- Smoke CTest and sharded/full CTest as approved.
- Product boot proof.
- Portable projection proof.
- Internal pilot release proof.

## DOE-00 Readiness

Not ready. Feature implementation remains blocked.

## Next Task

`MOVE-BULK-A-SKIPPED-REFERENCE-REFINEMENT`

## RESTRUCTURE-REPAIR-00 Update

RESTRUCTURE-REPAIR-00 ran a repair/proof pass and remains PARTIAL.

- Passing: AIDE, strict structural validators, focused RepoX, smoke CTest, native configure, build-only `ALL_BUILD`, product boot, portable projection, and internal pilot validators.
- Repaired: stale AppShell/client paths, integration metadata path, archive manifest paths, TestX fixture host-path literals, ops JSON warning leakage, and narrow doc contract references.
- Still blocking: full CTest, frozen contract hashes, expired overrides, replay hash mismatches, AuditX timeout cases, and 23 excepted former bad roots.
- DOE-00 readiness: no.
- Feature implementation authorized: no.
- Next task: `MOVE-BULK-A-SKIPPED-REFERENCE-REFINEMENT`.
