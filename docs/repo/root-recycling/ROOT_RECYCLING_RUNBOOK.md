Status: DERIVED
Last Reviewed: 2026-05-16
Supersedes: none
Superseded By: none

# Root Recycling Runbook

1. Choose a root family.
2. Inventory the root.
3. Classify files.
4. Scan references and sensitivity markers.
5. Generate a draft salvage map.
6. Review risks.
7. Approve a move map in a later task.
8. Apply a small wave only after approval.
9. Rewrite references only in the approved task.
10. Run validators/build/test as required.
11. Update exception ledgers.
12. Retire shims only after evidence.

First inventories and reconciliation are evidence only. Move-wave selection is separate from move-wave application. Content/package roots require identity scans; authority roots require authority scans; core/control/net require semantic scans; lib/libs require ABI/build scans.

AIDE-MOVE-01-PLAN note: move planning is still no-apply. The first draft plan may name exact source and target paths, reference rewrites, validation, rollback, and exception updates, but only a later gate can authorize an apply task. AIDE-MOVE-01-PLAN selects `ide/README.md` only; `ide/manifests/**` remains deferred.

AIDE-MOVE-01-APPLY note: apply tasks must consume a gate-scoped authorization and perform only the named move and named reference rewrites. The first apply moved `ide/README.md` to `docs/architecture/IDE_PROJECTIONS.md`, kept `ide/manifests/**` untouched, and left root exception retirement for a later explicitly approved task.

AIDE-MOVE-02-PLAN note: move planning may legitimately stop with no selected candidate. After the first move, the next preferred roots must not be forced into an apply plan if they contain active tooling, Python modules, machine-readable metadata, or high-reference surfaces instead of docs-only/evidence-only material.

BASELINE-00 note: RELEASE-00 is the structural regression baseline for future MOVE-FAMILY cleanup. Before any move-family apply task, the plan must name its risk tier, required validation commands, exact paths, rollback posture, generated-output policy, and comparison rule from `docs/repo/STRUCTURAL_REGRESSION_BASELINE.md` and `docs/repo/MOVE_FAMILY_REGRESSION_REQUIREMENTS.md`. Move apply remains unauthorized until a later gate approves exact scope. DOE-00 and feature work remain deferred until post-restructure proof passes.

MOVE-FAMILY-00-PLAN note: a family-level plan may return `BLOCKED` when no safe subset remains. For `governance/`, `meta/`, `performance/`, `validation/`, and `ide/`, the remaining files are active Python/tooling surfaces or machine-readable IDE projection manifests. Do not force a move gate until active-module destinations, reference rewrite scope, and IDE projection ownership are resolved.

MOVE-FAMILY-00-REFINE note: active-module refinement must split mixed roots by owner before a gate. `ide/manifests/**` should be planned as projection contract metadata under `contracts/projections`; `validation/**`, `meta/identity/**`, and `meta/stability/**` need shim-aware validator namespace planning; `governance/**` needs release/tool import proof; semantic `meta/**` and product/runtime `performance/**` remain preserve-current until their owners are explicit.

MOVE-FAMILY-00B-PLAN note: IDE manifest planning may proceed to a gate only for the three tracked source metadata files under `ide/manifests/**`. The target owner is `contracts/projections/ide/**`, created only by a later approved apply task. Generated `ide/manifests/*.projection.json` output is a separate ignored-output concern and must not be committed. Retire the `ide` source-layout exception only after all tracked files leave `ide/` and validators pass.

MOVE-FAMILY-00B-APPLY note: apply tasks may retire a source-root exception only after the tracked state and filesystem state both support it. The IDE manifest apply moved exactly three tracked source metadata files to `contracts/projections/ide/**`, applied only five gate-approved current-reference rewrites, removed only the empty `ide/` directory tree left by the move, and retired only `ide_root` after strict validators passed.
