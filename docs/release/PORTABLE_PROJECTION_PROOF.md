Status: DERIVED
Last Reviewed: 2026-05-17
Supersedes: none
Superseded By: none

# Portable Projection Proof

## Current Status

Portable projection proof is blocked.

POST-CONVERGE-12 did not generate or assemble a projection root because POST-CONVERGE-11 product boot proof is blocked at the RepoX readiness gate. Product boot commands were not run, and no accepted-warning ledger authorizes portable projection proof to proceed without that prerequisite.

## Proof Input Status

| Input | Status | Notes |
| --- | --- | --- |
| Native build proof | historical partial | Native binaries were previously produced locally but were not refreshed by POST-CONVERGE-11 or POST-CONVERGE-12. |
| Product boot proof | blocked | POST-CONVERGE-11 stopped before binary inspection or execution. |
| RepoX gate | blocked | Focused `inv_repox_rules` remains 20 failures / 5 warnings. |
| Portable projection output | not generated | No local projection root was created. |
| Release readiness | blocked | RELEASE-00 must not proceed. |

## Intended Local Proof Root

Future retries should use an ignored local proof root such as:

```text
.dominium.local/projections/post-converge-12/
```

Generated projection output must remain ignored/local and must not be committed.

## Required Inputs For Retry

- Focused RepoX pass or reviewed accepted-warning ledger.
- POST-CONVERGE-11 product boot proof with native binaries.
- Current native binary root.
- Distribution layout contract.
- Required install, release, semantic contract, component, profile, and verification manifests.
- Portable projection validator or equivalent manifest/structure verification.

## Current Blockers

- `product_boot_blocked`
- `repox_semantic_blocker`
- `no_accepted_warning_ledger`

## How To Retry

1. Complete `POST-CONVERGE-10P - Residual RepoX Governance and Source-Policy Remediation` or a reviewed acceptance gate.
2. Rerun POST-CONVERGE-11 and prove native product boot/help/status surfaces.
3. Rerun POST-CONVERGE-12 only after POST-CONVERGE-11 reports `PASS`, `PASS_WITH_WARNINGS`, or an explicit accepted sufficient status.

## Relationship To RELEASE-00

RELEASE-00 internal pilot release is not ready. A portable, self-describing projection root has not been generated or validated.

## Closeout Remediation Update

The prerequisite RepoX and native command-surface blockers have improved:

- Focused RepoX now passes with zero recorded warnings and failures.
- Native product command smoke passes for the five product binaries under `out/build/vs2026/verify/bin/`.

Portable projection proof is now locally proven:

- Projection root: `.dominium.local/projections/post-converge-12/v0.0.0-post-converge-12/win64/dominium`.
- Assembler: `tools/dist/tool_assemble_dist_tree.py`.
- Validator: `tools/validators/check_portable_projection.py`.
- Validator status: `proof_status: proven`, blockers: none.
- Native binaries included in projection `bin/`: `setup.exe`, `launcher.exe`, `client.exe`, `server.exe`, `tools.exe`.

The generated projection root is ignored/local and was not committed. This is not a public package, installer, tag, GitHub release, or release artifact publication.

## RELEASE-00 Consumer Update

The proven portable projection root was consumed by RELEASE-00 as the input for local internal pilot staging:

```text
.dominium.local/releases/internal-pilot-0/projection
```

The internal pilot validator confirms that the staged projection still contains the required install, release, and semantic contract manifests and the five native product binaries. The generated release staging root is local/ignored and was not committed.

## BASELINE-00 Update

BASELINE-00 freezes this portable projection as part of the structural regression baseline.

- Baseline HEAD: `0b631fc5f09f3d927a54e8312976b926d111a72e`.
- Projection root: `.dominium.local/projections/post-converge-12/v0.0.0-post-converge-12/win64/dominium`.
- Release consumer root: `.dominium.local/releases/internal-pilot-0/projection`.
- Required manifests and native binaries remain the comparison target for MOVE-FAMILY tasks.
- Generated projection output remains ignored/local and must not be committed.

Future content, package, profile, bundle, distribution, release, or build-sensitive move waves must rerun the portable projection validator or regenerate the projection through documented tooling before claiming success.

<!-- POST-RESTRUCTURE-00-BLOCKED -->

## POST-RESTRUCTURE-00 Blocked Proof Note

POST-RESTRUCTURE-00 did not run the full proof chain because MOVE-BULK-08 closure says full proof is not ready.

- Remaining former bad-root files: 1764.
- Deferred batches: B-G.
- Blocked batch: H.
- Ready for DOE-00: no.
- Next recommended task: `MOVE-BULK-A-SKIPPED-REFERENCE-REFINEMENT`.
