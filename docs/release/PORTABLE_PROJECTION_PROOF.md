Status: DERIVED
Last Reviewed: 2026-05-18
Supersedes: none
Superseded By: none

# Portable Projection Proof

## Current Status

Portable projection proof is locally proven.

RESTRUCTURE-REPAIR-00 validated the ignored projection root at `.dominium.local/projections/post-converge-12/v0.0.0-post-converge-12/win64/dominium` with `proof_status: proven` and no blockers. Historical POST-CONVERGE blocked notes are retained below for continuity.

## Proof Input Status

| Input | Status | Notes |
| --- | --- | --- |
| Native build proof | pass | Build-only `ALL_BUILD` produced the expected native binaries. |
| Product boot proof | pass | Strict product boot matrix smoke passed. |
| RepoX gate | pass | Focused `inv_repox_rules` passed. |
| Portable projection output | pass | Local ignored projection root validates with `proof_status: proven`. |
| Release readiness | local proof pass | Internal pilot validator passes; public release remains out of scope. |

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

None for the portable projection validator. DOE-00 remains blocked by broader full CTest and root-debt findings recorded in `docs/repo/RESTRUCTURE_REPAIR_STATUS.md`.

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

<!-- RESTRUCTURE-REPAIR-00 -->

## RESTRUCTURE-REPAIR-00 Portable Projection Update

`python tools/validators/check_portable_projection.py --repo-root . --projection-root .dominium.local/projections/post-converge-12/v0.0.0-post-converge-12/win64/dominium --json --strict` passed with `proof_status: proven` and no blockers.

Generated projection output remains ignored/local and uncommitted.
