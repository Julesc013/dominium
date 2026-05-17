Status: DERIVED
Last Reviewed: 2026-05-16
Supersedes: none
Superseded By: none

# First Wave Plan

## AIDE-ROOT-00 Through AIDE-ROOT-06 Result

The root recycling framework and five inventory waves were generated as no-apply evidence. AIDE-ROOT-06 selected a draft-only first planning candidate.

## Recommended First Planning Candidate

- Root: `ide`
- Subtree: `docs/architecture/IDE_PROJECTIONS.md` moved from `ide/README.md`; `ide/manifests/**` remains deferred
- Risk: low
- Apply allowed: false
- Approval status: not_approved

## Gate Note

AIDE-GATE-01 may authorize `AIDE-MOVE-01-PLAN` only. Move application remains unauthorized.

## AIDE-MOVE-01-PLAN Result

AIDE-MOVE-01-PLAN narrowed the first candidate to `ide/README.md` -> `docs/architecture/IDE_PROJECTIONS.md`. The manifest schema/examples under `ide/manifests/**` remain deferred. The plan is draft, not approved, and no-apply. `AIDE-GATE-02` may inspect the plan; move application remains unauthorized.

## AIDE-GATE-02 Result

AIDE-GATE-02 passed with warnings and authorizes only `AIDE-MOVE-01-APPLY` for `ide/README.md` -> `docs/architecture/IDE_PROJECTIONS.md`. All other moves remain unauthorized, and `ide/manifests/**` remains deferred.

## AIDE-MOVE-01-APPLY Result

AIDE-MOVE-01-APPLY moved `ide/README.md` to `docs/architecture/IDE_PROJECTIONS.md` and applied only the six planned reference rewrites. `ide/manifests/**` remains deferred and untouched, the `ide/` root exception was not retired, and the next recommended task is `AIDE-GATE-03`.

## AIDE-GATE-03 Result

AIDE-GATE-03 passed with warnings and verified the first move wave post-state. `AIDE-MOVE-02-PLAN` may proceed, but no move application is authorized.

## AIDE-MOVE-02-PLAN Result

AIDE-MOVE-02-PLAN reviewed the next preferred roots and did not select a second move candidate. After the IDE README move, the remaining preferred-root material is deferred machine-readable IDE metadata or active Python/tooling code. The draft plan is not approved, apply remains false, and the recommended next task is candidate refinement rather than an apply gate.

## AIDE-MOVE-02-REFINE Result

AIDE-MOVE-02-REFINE narrowed the search to single-file docs, historical/evidence files, README-style files, template scaffolds, and generated review artifacts. No candidate passed the low-risk filter. `templates/` contained the closest near-misses, but both files are template scaffolds with protected spec/XStack references and conversion fates. The recommended next task is `POST-CONVERGE-10F - Unit Annotation and RepoX Rule Remediation`, not `AIDE-GATE-04`.

## BASELINE-00 Result

RELEASE-00 is now frozen as the structural regression baseline before the next root cleanup sequence.

- Move apply remains unauthorized.
- The next task is `MOVE-FAMILY-00-PLAN - Governance, Meta, Performance, Validation, and IDE Cleanup Plan`.
- Future first-wave selection must use `docs/repo/STRUCTURAL_REGRESSION_BASELINE.md` and `docs/repo/MOVE_FAMILY_REGRESSION_REQUIREMENTS.md`.
- Generated release/projection/build/local outputs must remain ignored and uncommitted.
- DOE-00 and feature work remain deferred until MOVE-FAMILY cleanup and post-restructure proof pass.

## MOVE-FAMILY-00-PLAN Result

MOVE-FAMILY-00-PLAN inspected `governance/`, `meta/`, `performance/`, `validation/`, and `ide/` against BASELINE-00. No apply-ready move set was selected: `ide/README.md` was already moved by AIDE-MOVE-01, and the remaining material is active Python/tooling surface or machine-readable IDE projection metadata.

- Planned moves: 0.
- Apply allowed: false.
- Approval status: not_approved.
- Ready for `MOVE-FAMILY-00-GATE`: false.
- Recommended next task: `MOVE-FAMILY-00-REFINE-ACTIVE-MODULE-BOUNDARIES - Define ownership and consumer-safe destinations for active governance/meta/performance/validation modules and IDE projection manifests`.

## MOVE-FAMILY-00-REFINE Result

MOVE-FAMILY-00-REFINE-ACTIVE-MODULE-BOUNDARIES produced ownership boundary evidence and kept apply disabled.

- Active Python files found: 33.
- IDE manifest files found: 3.
- Clear next group: `ide/manifests/**` to be planned under `contracts/projections`.
- Validator-like groups: `validation/**`, `meta/identity/**`, and `meta/stability/**` need shim/import planning before any move.
- `performance/**` remains preserve-current because product/client/game code imports it.
- Ready for `MOVE-FAMILY-00-GATE`: false.
- Recommended next task: `MOVE-FAMILY-00B-PLAN - IDE Manifest Contract/Projection Ownership Plan`.

## MOVE-FAMILY-00B-PLAN Result

MOVE-FAMILY-00B-PLAN produced a no-apply draft plan for the remaining tracked IDE manifest source metadata.

- Planned moves: 3 tracked files from `ide/manifests/**` to `contracts/projections/ide/**`.
- Deferred tracked IDE manifest files: 0.
- Blocked files: 0.
- Ready for `MOVE-FAMILY-00B-GATE`: true.
- Apply allowed: false.
- The future apply task must keep generated IDE projection output ignored and may retire the `ide` source-layout exception only after `git ls-files ide` is empty and validators pass.

## MOVE-FAMILY-00B-GATE Result

MOVE-FAMILY-00B-GATE passed with warnings and authorizes only `MOVE-FAMILY-00B-APPLY` for the three planned `ide/manifests/**` to `contracts/projections/ide/**` moves. No files were moved, deleted, renamed, reference-rewritten, or exception-retired by the gate. All other MOVE-FAMILY waves remain unauthorized.

## MOVE-FAMILY-00B-APPLY Result

MOVE-FAMILY-00B-APPLY moved the three tracked IDE manifest files to `contracts/projections/ide/**`, applied the five approved reference rewrite groups, removed the empty `ide/` directory tree, and retired the `ide` source-layout exception after `git ls-files ide` became empty. All other MOVE-FAMILY moves remain unauthorized.

## MOVE-FAMILY-00B-PROOF Result

MOVE-FAMILY-00B-PROOF proved the first bad-root retirement.

- `git ls-files ide`: empty.
- Filesystem `ide/`: absent.
- `ide_root` exception: retired and accepted by strict validators.
- Active stale references to old tracked schema/example paths: none.
- Remaining old-path references are warning-only historical/planning/audit/AIDE/generated-output references.
- Next recommended task: `MOVE-FAMILY-00C-PLAN - Active Validation/Meta/Governance Tool Namespace Plan`.
