Status: DERIVED
Last Reviewed: 2026-05-18
Supersedes: none
Superseded By: none

# Internal Pilot Readiness

## Status

RELEASE-00 internal pilot staging is locally proven. DOE-00 remains blocked by broader restructure repair findings.

## Readiness Matrix

| Gate | Status | Evidence | Notes |
| --- | --- | --- | --- |
| Native build proof | pass | `docs/release/NATIVE_BINARY_PROOF.md` | Build-only proof produced the expected native binaries. |
| Product boot proof | pass | `docs/release/PRODUCT_BOOT_PROOF.md` | Strict product boot matrix smoke passed. |
| Portable projection proof | pass | `docs/release/PORTABLE_PROJECTION_PROOF.md` | Ignored projection root validates with `proof_status: proven`. |
| Package/release proof | not run | none | Public release, installer, and package generation remain out of scope. |
| RepoX gate | pass | `.aide/reports/RESTRUCTURE-REPAIR-00-validation.md` | Focused RepoX passed after archive allowlist repair. |

## Remaining Blockers

- Full CTest remains failing/incomplete.
- Root cleanup debt remains under active exceptions.
- Frozen hash, override, replay, and AuditX remediation remain separate blockers.

## Release Decision

Local internal pilot proof is valid for ignored staging only. Public release, installer, package publication, and DOE-00 remain out of scope for this proof.

Recommended next task:

```text
MOVE-BULK-A-SKIPPED-REFERENCE-REFINEMENT
```

## Closeout Remediation Update

RepoX and native command-surface readiness have improved since the blocked POST-CONVERGE-12 gate:

- Focused RepoX now passes.
- Native product command smoke now passes for `setup`, `launcher`, `client`, `server`, and `tools`.
- CTest smoke now passes 57/57.

RELEASE-00 remains blocked because portable projection proof has not yet produced or validated a local projection root. The next release-readiness task is `POST-CONVERGE-12 - Portable Projection Proof`; TEST-PERF sharding remains a separate validation-speed follow-up.

## Portable Projection Closeout Update

RELEASE-00 internal pilot preparation may now proceed with warnings:

- Focused RepoX passes.
- Native product command smoke passes for the five product binaries.
- Local ignored portable projection proof passes with `proof_status: proven`.
- The projection root includes required portable roots/manifests and the five native product binaries.

Remaining warnings:

- Full promotion CTest was not run.
- `cmake --build --preset verify` timed out during verification after producing the binaries.
- No public package, installer, tag, GitHub release, or release publication was generated.

Recommended next task:

```text
RELEASE-00 - Internal Pilot Release 0
```

## RELEASE-00 Update

Operating-environment MVP spine work may proceed with warnings:

- Internal Pilot Release 0 is staged under `.dominium.local/releases/internal-pilot-0`.
- The staging root includes the portable projection tree, release manifest, provenance, checksums, proof reports, warning ledger, runbook, and rollback notes.
- The strict internal pilot validator passes with no blockers and verifies 4718 checksum entries.
- The generated release staging root is ignored/local and was not committed.

Remaining warnings:

- Full promotion CTest was not run.
- No public package, installer, tag, GitHub release, upload, or release publication was created.

Recommended next task:

```text
DOE-00 - Dominium Operating Environment Doctrine and Boot Spine Plan
```

## BASELINE-00 Update

RELEASE-00 remains accepted as local internal pilot proof, but the immediate next repository task is now structural cleanup planning, not DOE-00.

- Baseline HEAD: `0b631fc5f09f3d927a54e8312976b926d111a72e`.
- Internal pilot release root: `.dominium.local/releases/internal-pilot-0`.
- Projection input: `.dominium.local/projections/post-converge-12/v0.0.0-post-converge-12/win64/dominium`.
- Strict internal pilot validation remains the release regression check for move families that touch release/projection prerequisites.
- Generated release/projection/build output remains ignored/local and must not be committed.
- DOE-00 and feature work are deferred until MOVE-FAMILY cleanup and post-restructure proof pass.

Recommended next task:

```text
MOVE-FAMILY-00-PLAN - Governance, Meta, Performance, Validation, and IDE Cleanup Plan
```

<!-- POST-RESTRUCTURE-00-BLOCKED -->

## POST-RESTRUCTURE-00 Blocked Proof Note

POST-RESTRUCTURE-00 did not run the full proof chain because MOVE-BULK-08 closure says full proof is not ready.

- Remaining former bad-root files: 1764.
- Deferred batches: B-G.
- Blocked batch: H.
- Ready for DOE-00: no.
- Next recommended task: `MOVE-BULK-A-SKIPPED-REFERENCE-REFINEMENT`.

<!-- RESTRUCTURE-REPAIR-00 -->

## RESTRUCTURE-REPAIR-00 Internal Pilot Readiness Update

The strict internal pilot validator passed against `.dominium.local/releases/internal-pilot-0` with no blockers or warnings. This preserves the local proof artifact only.

DOE-00 still may not proceed because full CTest and root-debt blockers remain outside the internal pilot staging proof.
