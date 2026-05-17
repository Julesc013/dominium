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

## MOVE-FAMILY-00B-PLAN Update

MOVE-FAMILY-00B-PLAN planned the tracked IDE manifest source-metadata migration without applying moves.

- Result: PASS_WITH_WARNINGS.
- Manifest files inspected: 3.
- Planned moves: 3.
- Target owner: `contracts/projections/ide/**`.
- Ready for `MOVE-FAMILY-00B-GATE`: true.
- Apply remains unauthorized.
- Generated IDE projection output under `ide/manifests/*.projection.json` remains generated/local output and must not be committed.
- Next recommended task: `MOVE-FAMILY-00B-GATE - IDE Manifest Projection Apply Readiness Gate`.

## MOVE-FAMILY-00B-GATE Update

MOVE-FAMILY-00B-GATE reviewed the draft IDE manifest projection plan and authorized only the next apply task.

- Result: PASS_WITH_WARNINGS.
- Planned moves reviewed: 3 tracked files from `ide/manifests/**` to `contracts/projections/ide/**`.
- Apply rewrite groups reviewed: 5.
- Target collision status: no tracked or filesystem target collisions found; `contracts/projections/ide/**` is planned for creation during apply.
- Exception condition: retire `ide` only if approved apply leaves `git ls-files ide` empty and validators pass.
- Authorized next task: `MOVE-FAMILY-00B-APPLY - Apply IDE Manifest Projection Migration`.
- Authorized scope: the three planned IDE manifest moves only.
- All other moves remain unauthorized.
- No files were moved, deleted, renamed, reference-rewritten, or exception-retired by the gate.

## MOVE-FAMILY-00B-APPLY Update

MOVE-FAMILY-00B-APPLY applied the scoped IDE manifest projection migration.

- Result: PASS_WITH_WARNINGS.
- Moves applied: 3.
- Rewrite groups applied: 5.
- `git ls-files ide`: empty.
- `ide` filesystem root: absent after empty directory cleanup.
- `ide_root` exception: retired.
- Active layout exception count: 31.
- Focused RepoX: passed after touched-doc status header repair.
- Next recommended task: `MOVE-FAMILY-00B-PROOF - IDE Root Retirement Proof`.
- All other root-family moves remain unauthorized.

## MOVE-FAMILY-00B-PROOF Update

MOVE-FAMILY-00B-PROOF proved the IDE root retirement.

- Result: PASS_WITH_WARNINGS.
- `git ls-files ide`: empty.
- Filesystem `ide/`: absent.
- `ide_root` exception: retired.
- Replacement manifests under `contracts/projections/ide/**`: tracked, present, JSON parse PASS.
- Active stale references to old tracked schema/example source paths: none.
- Focused RepoX: PASS.
- Next recommended task: `MOVE-FAMILY-00C-PLAN - Active Validation/Meta/Governance Tool Namespace Plan`.
- All other root-family moves remain unauthorized.

## MOVE-FAMILY-00C-PLAN Update - Active Tool Namespace Planning

- Result: BLOCKED.
- Target roots inspected: `validation/`, `meta/`, `governance/`, and `performance/`.
- Active Python files found: 33.
- Package init files: 14.
- Direct CLI entrypoints under target roots: 0.
- Active Python import files: validation 8, meta 104, governance 9, performance 4.
- Planned move count: 0.
- Shim-required candidate groups: `validation`, `meta.identity`, `meta.stability`, and `governance`.
- semantic/runtime `meta/**` and product/runtime `performance/**` remain preserve-current.
- No moves, deletes, renames, shims, import rewrites, reference rewrites, map applications, or exception retirements occurred.
- Next recommended task: `MOVE-FAMILY-00C-A-PLAN - Validation, Identity, and Stability Shim Contract Plan`.

## MOVE-FAMILY-00C-A-PLAN Update - Validation Shim Contract Planning

- Result: PASS_WITH_WARNINGS.
- Groups planned: `validation`, `meta.identity`, and `meta.stability`.
- Target namespaces: `tools.validators.validation`, `tools.validators.identity`, and `tools.validators.stability`.
- Planned future implementation moves: 7.
- Planned future temporary shim files: 7.
- Apply-phase import rewrites planned: 34.
- Temporary old-import allowlist entries: 10.
- Ready for `MOVE-FAMILY-00C-A-GATE`: true.
- No moves, deletes, renames, shims, import rewrites, reference rewrites, map applications, or exception retirements occurred.
- Next recommended task: `MOVE-FAMILY-00C-A-GATE - Validation, Identity, and Stability Shim Migration Gate`.

## MOVE-BULK-00-PLAN Update

MOVE-BULK-00-PLAN creates one global no-apply migration plan for all remaining tracked bad roots.

- Remaining bad roots inspected: 23.
- Tracked files under bad roots: 1,790.
- Initial gate-ready file count: 309.
- Deferred until batch gates: 1,481.
- Explicit blocked file count: 1.
- First ready batch: Batch A docs/evidence/archive-only.
- `ide/` remains retired and excluded from remaining bad-root planning.
- Apply remains unauthorized and feature work remains blocked.
- Next recommended task: `MOVE-BULK-00-GATE - Global Bad-Root Migration Gate`.
