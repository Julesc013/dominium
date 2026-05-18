Status: DERIVED
Last Reviewed: 2026-05-17
Supersedes: none
Superseded By: none

# MOVE-FAMILY Regression Requirements

## Status

- Task ID: BASELINE-00
- Source baseline: `docs/repo/STRUCTURAL_REGRESSION_BASELINE.md`
- Baseline HEAD: `0b631fc5f09f3d927a54e8312976b926d111a72e`
- Move apply authorized: false
- Feature work authorized: false
- Next authorized task: `MOVE-FAMILY-00-PLAN - Governance, Meta, Performance, Validation, and IDE Cleanup Plan`

## Purpose

This document defines the validation and comparison rules that every MOVE-FAMILY planning, apply, and proof task must use while physically cleaning root folders. It protects the RELEASE-00 internal pilot proof from structural cleanup regressions.

## Move Family Risk Classes

| Family | Risk class | Scope posture |
| --- | --- | --- |
| MOVE-FAMILY-00 | governance/meta/performance/validation/IDE cleanup planning | plan only unless a later gate authorizes apply |
| MOVE-FAMILY-01 | docs/content/template cleanup | low to medium risk depending on references |
| MOVE-FAMILY-02 | content/package/profile/bundle/projection-sensitive cleanup | high risk for packaging and projection |
| MOVE-FAMILY-03 | contract/security/safety/source-policy cleanup | high risk for governance and validators |
| MOVE-FAMILY-04 | core/control/net/runtime/build-sensitive cleanup | high risk for build, product boot, and CTest |
| MOVE-FAMILY-05 | lib/libs/ABI/UI-bind cleanup | high risk for ABI, generated UI binding, and product boot |
| MOVE-FAMILY-06 | AIDE/RepoX/TestX/AuditX wrapper cleanup | high risk for tool equivalence and evidence integrity |
| MOVE-FAMILY-07 | post-restructure proof | promotion-level restructuring proof |

## Required Validation by Family

| Family | Required minimum validation |
| --- | --- |
| MOVE-FAMILY-00 | Tier 0 plus focused docs/root checks; no apply unless a later gate says so |
| MOVE-FAMILY-01 | Tier 0 plus docs/content/template checks and focused reference scans |
| MOVE-FAMILY-02 | Tier 0 plus content/package/profile validators, portable projection proof, internal pilot release proof, and smoke CTest |
| MOVE-FAMILY-03 | Tier 0 plus focused RepoX, contract validators, security validators, and safety/source-policy validators |
| MOVE-FAMILY-04 | Tier 0 plus CMake configure/build, focused CTest, smoke CTest, product boot proof, portable projection proof, and internal pilot proof |
| MOVE-FAMILY-05 | Tier 0 plus CMake configure/build, ABI boundary checks, UI bind checks, focused CTest, smoke CTest, and product boot proof |
| MOVE-FAMILY-06 | Tier 0 plus affected AIDE wrappers and RepoX/TestX/AuditX equivalence where available |
| MOVE-FAMILY-07 | Tier 4 full post-restructure proof |

## Required Proof by Family

| Proof | Families that require it |
| --- | --- |
| Generated-output ignored/staging proof | all families |
| Strict repo/root/distribution/component validators | all families |
| Focused RepoX | MOVE-FAMILY-00 if root policy is touched; MOVE-FAMILY-01+ when references or governance are touched |
| Smoke CTest | MOVE-FAMILY-01+ when quick and available; required for MOVE-FAMILY-02 through MOVE-FAMILY-07 |
| Portable projection proof | MOVE-FAMILY-02, MOVE-FAMILY-04, MOVE-FAMILY-07; also any task touching distribution/package/profile/bundle/projection paths |
| Internal pilot release proof | MOVE-FAMILY-02, MOVE-FAMILY-04, MOVE-FAMILY-07; also any task touching release staging prerequisites |
| Native build proof | MOVE-FAMILY-04, MOVE-FAMILY-05, MOVE-FAMILY-07 |
| Product boot proof | MOVE-FAMILY-04, MOVE-FAMILY-05, MOVE-FAMILY-07 |
| Full or accepted-sharded CTest | MOVE-FAMILY-07 before restructuring closeout |

## Rollback Requirements

- Every apply task must name the exact paths it is allowed to move before it runs.
- Rollback must restore the pre-apply tracked path graph without touching generated ignored proof roots.
- No task may use `git reset --hard`, rebase, amend, or discard unrelated work to recover.
- If a move regresses a required tier and cannot be fixed within scope, the task must stop, record blocker evidence, and leave generated outputs uncommitted.
- Exception ledgers must shrink or remain justified; they must not grow without a documented reason and gate.

## Generated Output Policy

- Do not commit `.dominium.local/**`.
- Do not commit `.aide.local/**`.
- Do not commit generated release bundle bytes, portable projection output, build output, installer output, package output, or local caches.
- Future tasks may regenerate release/projection output only through documented tooling and must record command, root, manifest, checksum, and validator evidence.
- Generated roots absent on a later machine are warning-only until a task claims projection/release proof; then absence must be resolved by documented regeneration or recorded as a blocker.

## Exception Ledger Policy

- Remaining root exceptions must shrink or stay justified.
- A new top-level root is a blocker unless the root constitution and task scope explicitly permit it.
- Ownership-sensitive roots must follow `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`.
- `fields/` must not be collapsed into `field/`.
- `schema/` and `schemas/` must not be treated as interchangeable semantic owners.
- `packs/` and `data/packs/` remain scoped ownership surfaces with residual quarantine.
- `specs/reality/` remains canonical over `data/reality/`.
- `docs/planning/` remains canonical over `data/planning/`.

## Before Starting DOE-00

DOE-00 and feature/operating-environment MVP work remain deferred until:

1. MOVE-FAMILY cleanup planning starts with `MOVE-FAMILY-00-PLAN`.
2. Authorized move apply waves complete without baseline regression.
3. MOVE-FAMILY-07 or equivalent post-restructure proof passes.
4. Native build, product boot, portable projection, and internal pilot proof are refreshed or explicitly accepted after restructuring.

Until then, the immediate next task is:

```text
MOVE-FAMILY-00-PLAN - Governance, Meta, Performance, Validation, and IDE Cleanup Plan
```

## MOVE-BULK-01 Regression Note

MOVE-BULK-01 applied a Batch A safe subset only.

- Applied moves: 26 docs/evidence/archive-only files.
- Skipped files: 283 files with active/current exact references.
- Reference rewrites: 0.
- Import rewrites: 0.
- Exception retirements: 0.
- `data/` remains a tracked root, so its exception remains justified.

The result preserves the BASELINE-00 rule that apply tasks must skip unsafe paths instead of forcing broad rewrites outside their gate.

## MOVE-FAMILY-00-PLAN Outcome

MOVE-FAMILY-00-PLAN produced a blocked draft rather than an apply-ready gate package.

- Planned moves: 0.
- Ready for `MOVE-FAMILY-00-GATE`: false.
- Reason: the remaining target-family files are active Python/tooling import surfaces or machine-readable IDE projection metadata.
- Apply remains unauthorized.
- Next task: `MOVE-FAMILY-00-REFINE-ACTIVE-MODULE-BOUNDARIES - Define ownership and consumer-safe destinations for active governance/meta/performance/validation modules and IDE projection manifests`.

The future validation posture remains Tier 0 plus focused RepoX for any eventual family-00 apply scope. If active tooling moves are included, affected wrapper/tool validation and consumer proof become required.

## MOVE-FAMILY-00-REFINE Outcome

MOVE-FAMILY-00-REFINE-ACTIVE-MODULE-BOUNDARIES refined the blocked plan into ownership groups.

- `ide/manifests/**`: plan next under `contracts/projections` with manifest contract and validator proof.
- `validation/**`, `meta/identity/**`, and `meta/stability/**`: plan later under `tools/validators` with temporary shim/import proof.
- `governance/**`: plan later under the repo/tooling slot with release/setup/archive/generated/dist/governance import proof.
- semantic/runtime `meta/**` and product/runtime `performance/**`: preserve-current until owner-specific plans exist.

No group is apply-ready. The immediate next planning task is:

```text
MOVE-FAMILY-00B-PLAN - IDE Manifest Contract/Projection Ownership Plan
```

## MOVE-FAMILY-00B-PLAN Outcome

MOVE-FAMILY-00B-PLAN produced a gate-ready no-apply draft for the IDE manifest source metadata.

- Planned moves: 3 tracked files.
- Target owner: `contracts/projection/ide/**`.
- Deferred tracked files: 0.
- Blocked files: 0.
- Ready for `MOVE-FAMILY-00B-GATE`: true.
- Apply remains unauthorized until the gate approves exact moves and reference rewrites.

The later apply task must run Tier 0 plus focused RepoX, manifest JSON/schema parsing, stale-reference scans, and generated-output ignored/staging proof. Full CTest, full eval, CMake configure/build, product binary execution, package/release generation, portable projection proof, and internal pilot proof remain out of scope unless generated-output producers or release/projection inputs change.

Immediate next task:

```text
MOVE-FAMILY-00B-GATE - IDE Manifest Projection Apply Readiness Gate
```

## MOVE-FAMILY-00B-APPLY Outcome

MOVE-FAMILY-00B-APPLY completed the IDE manifest source migration.

- Moves applied: 3.
- Rewrite groups applied: 5.
- `ide` tracked files after apply: none.
- `ide` source-layout exception: retired.
- Required follow-up: `MOVE-FAMILY-00B-PROOF - IDE Root Retirement Proof`.

Future MOVE-FAMILY tasks must continue to use Tier 0 plus risk-specific validators from this file. This apply does not authorize governance, meta, performance, validation, package, release, runtime, or feature moves.

## MOVE-FAMILY-00B-PROOF Outcome

MOVE-FAMILY-00B-PROOF proved the IDE root retirement.

- `git ls-files ide`: empty.
- Filesystem `ide/`: absent.
- `ide_root` source-layout exception: retired and accepted by strict validators.
- Replacement manifest files under `contracts/projection/ide/**`: tracked, present, JSON parse PASS.
- Active stale references to old tracked schema/example source paths: none.
- Remaining old-path references: historical, planning, audit, AIDE evidence, root-recycling history, or generated-output references.
- Baseline validation: Tier 0, strict validators, docs/build/UI/ABI checks, focused RepoX, manifest parsing, and generated-output ignored/staging checks passed with known warnings.

Next recommended task:

```text
MOVE-FAMILY-00C-PLAN - Active Validation/Meta/Governance Tool Namespace Plan
```

## MOVE-FAMILY-00C-PLAN Outcome

MOVE-FAMILY-00C-PLAN produced a blocked active-tool namespace plan.

- Target roots inspected: `validation/`, `meta/`, `governance/`, and `performance/`.
- Active Python files: 33.
- Apply-ready move count: 0.
- Future candidate files requiring shim/import planning: 9.
- Preserve-current/deferred files: 24.
- Ready for `MOVE-FAMILY-00C-GATE`: false.

Any future active-tool apply must add to Tier 0:

- focused RepoX;
- affected validator commands;
- py_compile and import smoke for moved modules and modified consumers;
- stale-import scans for old public import surfaces;
- smoke CTest if active validators or AppShell import paths are touched.

Next recommended task:

```text
MOVE-FAMILY-00C-A-PLAN - Validation, Identity, and Stability Shim Contract Plan
```

## MOVE-FAMILY-00C-A-PLAN Outcome

MOVE-FAMILY-00C-A-PLAN produced a gate-ready shim contract plan for `validation`, `meta.identity`, and `meta.stability`.

- Planned future implementation moves: 7.
- Planned future temporary shim files: 7.
- Apply-phase import rewrites: 34.
- Temporary old-import allowlist entries: 10.
- Target namespaces: `tools.validators.validation`, `tools.validators.identity`, and `tools.validators.stability`.
- Ready for `MOVE-FAMILY-00C-A-GATE`: true.

Any future 00C-A apply must additionally run:

- py_compile for moved modules and shim files;
- old-import shim smoke checks;
- new-import target namespace smoke checks;
- affected validator smoke checks;
- stale old-import static check;
- focused RepoX;
- smoke CTest if active validator or AppShell import paths are changed.

Next recommended task:

```text
MOVE-FAMILY-00C-A-GATE - Validation, Identity, and Stability Shim Migration Gate
```

## MOVE-BULK-00-PLAN Outcome

MOVE-BULK-00-PLAN replaces the remaining MOVE-FAMILY micro-plan queue with one global no-apply migration plan.

- Remaining tracked bad-root files: 1,790.
- Initial gate-ready subset: 309 files in Batch A docs/evidence/archive-only.
- Deferred until batch gates: 1,481 files.
- Explicit blocked action: `docs/development/libraries/CMakeLists.txt` until a CMake/build-focused ABI gate approves target rewiring.
- `ide/` remains retired and excluded from remaining tracked bad-root planning.
- No moves, deletes, renames, shims, import rewrites, reference rewrites, map applications, or exception retirements occurred.

Batch validation floors:

- Batch A: Tier 0.
- Batch B and E: Tier 0 plus Tier 1 import/static checks where active Python moves are involved.
- Batch C and D: Tier 0 plus Tier 2 content, identity, contract, projection, release, or authority validators as applicable.
- Batch F and G: Tier 0 plus Tier 3 build, ABI, CTest, product boot, and projection proof as applicable.
- Batch H: Tier 4 post-restructure proof.

Next recommended task:

```text
MOVE-BULK-00-GATE - Global Bad-Root Migration Gate
```

## MOVE-BULK-00-GATE Outcome

MOVE-BULK-00-GATE passed with warnings.

- Authorized batch: Batch A docs/evidence/archive-only.
- Authorized next task: `MOVE-BULK-01-APPLY-DOCS-ARCHIVE`.
- Deferred batches: B, C, D, E, F, and G.
- Blocked batch: H until prior apply/proof completion.
- Feature work remains unauthorized.
- No moves, deletes, renames, shims, import rewrites, reference rewrites, map applications, or exception retirements occurred.

Batch A apply must run Tier 0 validation plus stale-reference classification. Higher-risk batches remain subject to the stronger tiers defined above.

<!-- MOVE-BULK-08-CLOSURE -->

## MOVE-BULK-08 Final Exception Closure

MOVE-BULK-08 records a partial closure snapshot rather than a clean final closeout.

- Remaining tracked bad-root files: 1764.
- Roots still tracked: 23.
- Roots retired or empty: ide.
- Exceptions retired or narrowed by closure: 0.
- New shims created by closure: 0.
- Ready for `POST-RESTRUCTURE-00-FULL-PROOF`: no.
- Recommended next task: `MOVE-BULK-A-SKIPPED-REFERENCE-REFINEMENT`, or the next explicit batch gate.

<!-- POST-RESTRUCTURE-00-BLOCKED -->

## POST-RESTRUCTURE-00 Blocked Proof Note

POST-RESTRUCTURE-00 did not run the full proof chain because MOVE-BULK-08 closure says full proof is not ready.

- Remaining former bad-root files: 1764.
- Deferred batches: B-G.
- Blocked batch: H.
- Ready for DOE-00: no.
- Next recommended task: `MOVE-BULK-A-SKIPPED-REFERENCE-REFINEMENT`.

<!-- RESTRUCTURE-REPAIR-00 -->

## RESTRUCTURE-REPAIR-00 Regression Update

The repair pass establishes the current partial regression posture:

- Required green before DOE-00: strict structural validators, AIDE, focused RepoX, smoke CTest, native configure/build, product boot, portable projection, internal pilot, and a resolved full CTest strategy.
- Currently green: all lanes above except full CTest.
- Currently blocking: full CTest semantic/policy failures, AuditX timeouts, frozen hash drift, expired overrides, replay hash mismatches, and remaining former bad-root debt.
- Future repair tasks must not weaken validators or mark these failures warning-only without review.
