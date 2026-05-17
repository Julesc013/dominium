Status: DERIVED
Last Reviewed: 2026-05-17
Supersedes: none
Superseded By: none

# Structural Regression Baseline

## Status

- Task ID: BASELINE-00
- Baseline source: RELEASE-00 internal pilot release proof
- Baseline commit/HEAD: `0b631fc5f09f3d927a54e8312976b926d111a72e`
- origin/main at freeze: `0b631fc5f09f3d927a54e8312976b926d111a72e`
- Branch: `main`
- Scope: freeze baseline evidence and requirements only; no source-root move, delete, rename, alias, move map, salvage map, release publication, tag, upload, installer, package publication, feature work, or product behavior change.

## Purpose

BASELINE-00 freezes RELEASE-00 as the structural regression baseline before MOVE-FAMILY physical cleanup waves. Future move tasks must preserve the build, product boot, portable projection, internal pilot staging, validator, and warning posture recorded here.

This baseline exists because Dominium now has a meaningful local internal pilot release proof. Directory cleanup must not destroy the first working proof of native binaries, portable projection, release staging, manifests, checksums, provenance, proof reports, runbook, rollback notes, and ignored generated-output discipline.

## Baseline Artifacts

| Artifact | Path | Required? | Notes |
| --- | --- | --- | --- |
| RELEASE-00 audit | `docs/repo/audits/RELEASE_00_INTERNAL_PILOT_RELEASE.md` | yes | Records internal pilot proof as `PASS_WITH_WARNINGS`. |
| Internal pilot release doc | `docs/release/INTERNAL_PILOT_RELEASE_0.md` | yes | Consumer-facing local release proof summary. |
| Internal pilot readiness | `docs/release/INTERNAL_PILOT_READINESS.md` | yes | Historical readiness and RELEASE-00 closeout status. |
| Native binary proof | `docs/release/NATIVE_BINARY_PROOF.md` | yes | Records native product binary proof and warnings. |
| Product boot proof | `docs/release/PRODUCT_BOOT_PROOF.md` | yes | Records product command-surface boot proof and limits. |
| Portable projection proof | `docs/release/PORTABLE_PROJECTION_PROOF.md` | yes | Records local ignored portable projection proof. |
| RELEASE-00 status | `.aide/reports/RELEASE-00-status.md` | yes | Local-only release staging status. |
| RELEASE-00 validation | `.aide/reports/RELEASE-00-validation.md` | yes | Prior validation matrix. |
| RELEASE-00 blockers | `.aide/reports/RELEASE-00-blockers.md` | yes | No RELEASE-00 blockers remain. |
| RELEASE-00 results JSON | `.aide/reports/RELEASE-00-internal-pilot-results.json` | yes | Machine-readable release proof summary. |
| RELEASE-00 tree JSON | `.aide/reports/RELEASE-00-release-tree.json` | yes | Machine-readable release tree summary. |
| BASELINE-00 audit | `docs/repo/audits/BASELINE_00_RELEASE_STRUCTURAL_REGRESSION_BASELINE.md` | yes | This freeze task audit. |
| BASELINE-00 JSON | `.aide/reports/BASELINE-00-structural-regression-baseline.json` | yes | Machine-readable baseline command and warning state. |

## Generated Local Outputs

| Root | Status | Ignored rule | Commit policy |
| --- | --- | --- | --- |
| `.dominium.local/releases/internal-pilot-0` | present | `.gitignore:41:/.dominium.local/` | must remain local and uncommitted |
| `.dominium.local/projections/post-converge-12/` | present | `.gitignore:41:/.dominium.local/` | must remain local and uncommitted |
| `.dominium.local/build/` | present | `.gitignore:41:/.dominium.local/` | must remain local and uncommitted |
| `.aide.local/` | present | `.gitignore:268:.aide.local/` | must remain local and uncommitted |

`git ls-files .dominium.local .aide.local` returned no tracked paths during BASELINE-00 intake.

## Release Proof State

- Release root: `.dominium.local/releases/internal-pilot-0`
- Projection input: `.dominium.local/projections/post-converge-12/v0.0.0-post-converge-12/win64/dominium`
- Release files: 4719 generated local files
- Checksums: `manifest/checksums.sha256`, 4718 entries
- Required manifests present:
  - `manifest/internal_pilot_release.manifest.json`
  - `manifest/provenance.json`
  - `projection/install.manifest.json`
  - `projection/release.manifest.json`
  - `projection/semantic_contract_registry.json`
- Proof reports present:
  - `proof/native_binary_proof.md`
  - `proof/product_boot_proof.md`
  - `proof/portable_projection_proof.md`
  - `proof/warning_ledger.md`
  - `proof/latest_dominium_status.md`
  - `proof/validation_report.json`
- Native binaries present in release staging:
  - `projection/bin/setup.exe`
  - `projection/bin/launcher.exe`
  - `projection/bin/client.exe`
  - `projection/bin/server.exe`
  - `projection/bin/tools.exe`

The generated staging manifest records stager-time `repo_head` `c7d0a1a1b4d92a127bfb58cb740d4d177131f213` and stager-time `origin_main` `7b9068bd421d1fa4ae872fdda598d412313548fe`. The tracked BASELINE-00 freeze commit is later because RELEASE-00 committed proof evidence and the follow-up commit-check disposition after staging. Future comparisons must preserve both facts.

## Proof Inputs

| Input | Baseline posture | Required future comparison |
| --- | --- | --- |
| Native binary proof | accepted with warnings | Product binaries remain present or are regenerated through documented tooling before proof claims. |
| Product boot proof | accepted command-surface smoke | Product command surfaces for setup, launcher, client, server, and tools must not regress for relevant move classes. |
| Portable projection proof | proven local ignored projection | Projection manifests, native binaries, and validator status must remain equivalent or better. |
| Internal pilot release proof | strict validator passed | Release manifests, checksums, proof reports, provenance, and generated-output policy must remain equivalent or better. |
| Focused RepoX | passed in RELEASE-00 evidence | Future Tier 1+ tasks must not reintroduce RepoX blockers. |
| Smoke CTest | 57/57 passed in RELEASE-00 evidence | Future Tier 1+ tasks must preserve smoke status or record a blocking regression. |
| Strict repo/root/distribution/component validators | passed | Tier 0 required after every move family. |
| Docs/build/UI/ABI checks | passed | Tier 0 required after every move family. |

## Known Warnings

- Full promotion CTest was not run for RELEASE-00 or BASELINE-00.
- Full eval was not run.
- No public package, installer, tag, GitHub release, upload, or release publication was created.
- Generated release, projection, build, and local AIDE outputs remain ignored local proof evidence and must not be committed.
- A prior full `cmake --build --preset verify` verification phase timed out after producing native binaries; this remains a validation-speed follow-up, not a release proof blocker.
- Stager-time release manifest provenance records earlier RELEASE-00 input commits than the BASELINE-00 freeze HEAD; this is expected because the release tree was not regenerated during baseline freeze.
- Older historical sections in POST-CONVERGE proof docs remain as history and are superseded by later closeout and BASELINE-00 updates.

## Regression Tiers

| Tier | Required after | Minimum commands/proofs |
| --- | --- | --- |
| Tier 0 | every MOVE-FAMILY wave | AIDE doctor/validate/test/selftest/tools/roots/repo, AIDE latest commit check, strict repo/root/distribution/component validators, docs sanity, build target boundaries, UI shell purity, ABI boundaries, generated-output ignored/staging checks, git diff checks |
| Tier 1 | medium-risk docs/tooling moves | Tier 0 plus focused RepoX, smoke CTest if available, and affected AIDE wrapper command if any |
| Tier 2 | content/package/profile/bundle moves | Tier 0 plus portable projection validator, internal pilot release validator, content/package/profile validators if present, and smoke CTest |
| Tier 3 | core/control/net/lib/libs/runtime/build-sensitive moves | Tier 0 plus CMake configure/build, focused CTest, smoke CTest, product boot proof, portable projection proof, and internal pilot proof |
| Tier 4 | before declaring restructuring complete | full or accepted-sharded CTest, post-restructure layout audit, native build proof, product boot proof, portable projection proof, and internal pilot rebuild/staging validation |

## Blocking Regressions

- Any Tier 0 required validator failure not already classified as warning-only in this baseline.
- Internal pilot validator failure when the release proof is required by the move family risk class.
- Portable projection validator failure when projection proof is required by the move family risk class.
- Missing release manifests, proof reports, provenance, checksums, or required product binaries without documented regeneration and validation.
- Any generated release/projection/build/local output staged or committed.
- Any new top-level root, active path alias, root move, delete, rename, move map, or salvage map outside the explicit task scope.
- Any product ID, pack ID, profile ID, bundle ID, semantic contract ID, virtual-root ID, package ID, or release ID change outside explicit reviewed scope.
- Known warnings worsening into hard failures, growing without disposition, or being hidden from the warning ledger.
- Root exceptions growing casually or unresolved ownership-sensitive roots being collapsed without review.
- Public release, tag, GitHub release, upload, installer, or package publication performed by a move-family task.

## Warning-Only Baseline Conditions

- Full CTest and full eval not run, unless the future task is Tier 4 or explicitly requires promotion proof.
- No public release artifacts created, unless the future task is a release-publication task.
- Generated release/projection output absent on a later machine, if the tracked proof docs exist and documented tooling can regenerate and validate it when needed.
- Historical proof-doc blocked sections remain visible, if later closeout and BASELINE-00 sections identify the current accepted state.
- Stager-time provenance commit differs from the BASELINE-00 freeze commit, if both are recorded and no regeneration claim is made.

## How Future Move Tasks Use This

Every MOVE-FAMILY plan/apply/proof task must:

1. State its risk tier and required command set before applying changes.
2. Compare current HEAD and generated proof state against BASELINE-00.
3. Run the required tier commands after the move.
4. Record whether release/projection roots were reused, absent, or regenerated.
5. Prove generated outputs stayed ignored and uncommitted.
6. Classify every deviation as blocking or warning-only using this file and `docs/repo/MOVE_FAMILY_REGRESSION_REQUIREMENTS.md`.
7. Stop before DOE-00 or feature work until MOVE-FAMILY cleanup and post-restructure proof pass.

Immediate next task:

```text
MOVE-FAMILY-00-PLAN - Governance, Meta, Performance, Validation, and IDE Cleanup Plan
```
