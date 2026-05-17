# Latest Dominium Status

Status: DERIVED
Last Reviewed: 2026-05-17
Supersedes: none
Superseded By: none

## Current Position

Focused RepoX is clean after the residual closeout remediation. Direct RepoX and canonical CTest focused `inv_repox_rules` both pass with zero recorded RepoX warnings and zero RepoX failures.

Native product command-surface smoke was run locally against `out/build/vs2026/verify/bin/` for `setup.exe`, `launcher.exe`, `client.exe`, `server.exe`, and `tools.exe`. Each returned exit code 0 for `--help`, `--version`, `--status`, and `--smoke`.

Canonical CTest discovery reports 493 tests, and `ctest --preset verify -L smoke --output-on-failure --timeout 300` passes 57/57. The full promotion build/test lane still needs wall-time partitioning: a prior `cmake --build --preset verify` run timed out during verification after producing the native binaries.

A local ignored portable projection root has been generated and validated:

```text
.dominium.local/projections/post-converge-12/v0.0.0-post-converge-12/win64/dominium
```

`tools/validators/check_portable_projection.py` reports `proof_status: proven` with no blockers. The generated projection `bin/` contains the five native product binaries and portable wrappers.

RELEASE-00 internal pilot staging now passes with warnings. The local ignored internal pilot root is:

```text
.dominium.local/releases/internal-pilot-0
```

The staging root contains the portable projection, internal pilot manifest, provenance, checksums, proof reports, warning ledger, runbook, and rollback notes. The strict internal pilot validator passes with no blockers and verifies 4718 checksum entries.

Public package/release generation, installer generation, tag creation, upload, and full promotion CTest remain not run.

## Next Recommended Task

`DOE-00 - Dominium Operating Environment Doctrine and Boot Spine Plan`, with `TEST-PERF-01 - CTest Sharding and Slow-Test Baseline` as the parallel validation-speed follow-up.

## BASELINE-00 Update

RELEASE-00 is now frozen as the structural regression baseline for MOVE-FAMILY cleanup waves.

- Baseline HEAD: `0b631fc5f09f3d927a54e8312976b926d111a72e`.
- Internal pilot release root: `.dominium.local/releases/internal-pilot-0`.
- Portable projection root: `.dominium.local/projections/post-converge-12/v0.0.0-post-converge-12/win64/dominium`.
- Generated release/projection/build/local outputs remain ignored and uncommitted.
- Move apply is not authorized by BASELINE-00.
- DOE-00 and feature work are deferred until MOVE-FAMILY cleanup and post-restructure proof pass.

## Next Recommended Task After BASELINE-00

`MOVE-FAMILY-00-PLAN - Governance, Meta, Performance, Validation, and IDE Cleanup Plan`.

## MOVE-FAMILY-00-PLAN Update

The first family-level cleanup plan inspected `governance/`, `meta/`, `performance/`, `validation/`, and `ide/` against BASELINE-00 task commit `6ed2516ea9570bd54cdd3f1d94ed347f48cf6447`.

- Result: BLOCKED.
- Planned moves: 0.
- Deferred files: 36.
- Ready for `MOVE-FAMILY-00-GATE`: false.
- No files were moved, deleted, renamed, or rewritten.
- Remaining target-family material is active Python/tooling surface or machine-readable IDE projection metadata.
- Next recommended task: `MOVE-FAMILY-00-REFINE-ACTIVE-MODULE-BOUNDARIES - Define ownership and consumer-safe destinations for active governance/meta/performance/validation modules and IDE projection manifests`.

## MOVE-FAMILY-00-REFINE Update

MOVE-FAMILY-00-REFINE-ACTIVE-MODULE-BOUNDARIES refined the blocked plan into owner groups without applying moves.

- Result: PASS_WITH_WARNINGS.
- Active Python files found: 33.
- IDE manifest files found: 3.
- Preferred IDE manifest owner: `contracts/projections`.
- Validator namespace candidates: `validation/**`, `meta/identity/**`, and `meta/stability/**`, all requiring temporary shim/import planning.
- Preserve-current groups: semantic/runtime `meta/**` and product/runtime `performance/**`.
- Ready for `MOVE-FAMILY-00-GATE`: false.
- Next recommended task: `MOVE-FAMILY-00B-PLAN - IDE Manifest Contract/Projection Ownership Plan`.
