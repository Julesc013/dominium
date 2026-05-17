Status: DERIVED
Last Reviewed: 2026-05-17
Supersedes: none
Superseded By: none

# Internal Pilot Readiness

## Status

RELEASE-00 internal pilot release is blocked.

## Readiness Matrix

| Gate | Status | Evidence | Notes |
| --- | --- | --- | --- |
| Native build proof | partial historical | `docs/release/NATIVE_BINARY_PROOF.md` | Binaries were previously produced locally, but this was not refreshed by POST-CONVERGE-11 or POST-CONVERGE-12. |
| Product boot proof | blocked | `docs/release/PRODUCT_BOOT_PROOF.md` | POST-CONVERGE-11 stopped at the RepoX readiness gate; product commands run: 0. |
| Portable projection proof | blocked | `docs/release/PORTABLE_PROJECTION_PROOF.md` | POST-CONVERGE-12 did not generate projection output. |
| Package/release proof | not run | none | Public release, installer, and package generation remain out of scope. |
| RepoX gate | blocked | `.aide/reports/POST-CONVERGE-11-blockers.md` | Focused RepoX remains 20 failures / 5 warnings. |

## Remaining Blockers

- Resolve or explicitly accept the remaining non-proof RepoX governance/source-policy failures.
- Rerun native product boot proof after the RepoX gate allows it.
- Generate and validate a portable projection root after product boot proof succeeds or is explicitly accepted.

## Release Decision

RELEASE-00 must not proceed from the current state.

Recommended next task:

```text
POST-CONVERGE-10P - Residual RepoX Governance and Source-Policy Remediation
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
