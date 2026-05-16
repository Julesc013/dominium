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
