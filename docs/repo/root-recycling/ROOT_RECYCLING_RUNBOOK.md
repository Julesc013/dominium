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

MOVE-FAMILY-00B-PLAN note: IDE manifest planning may proceed to a gate only for the three tracked source metadata files under `ide/manifests/**`. The target owner is `contracts/projection/ide/**`, created only by a later approved apply task. Generated `ide/manifests/*.projection.json` output is a separate ignored-output concern and must not be committed. Retire the `ide` source-layout exception only after all tracked files leave `ide/` and validators pass.

MOVE-FAMILY-00B-APPLY note: apply tasks may retire a source-root exception only after the tracked state and filesystem state both support it. The IDE manifest apply moved exactly three tracked source metadata files to `contracts/projection/ide/**`, applied only five gate-approved current-reference rewrites, removed only the empty `ide/` directory tree left by the move, and retired only `ide_root` after strict validators passed.

MOVE-FAMILY-00B-PROOF note: proof tasks must verify root retirement after apply before another family move starts. The IDE proof confirmed `git ls-files ide` is empty, filesystem `ide/` is absent, `ide_root` is retired, strict validators and focused RepoX pass, and old `ide/manifests/**` references are only historical/planning/audit/AIDE/generated-output references. No new apply authorization is granted by the proof.

MOVE-FAMILY-00C-PLAN note: active Python roots must not be moved by name alone. The validation/meta/governance candidates require a shim contract, stale-import policy, affected-consumer proof, and focused RepoX before any gate. `performance/**` and semantic/runtime `meta/**` are preserve-current until runtime/domain ownership plans exist.

MOVE-FAMILY-00C-A-PLAN note: validator-like active packages may proceed to a gate only with an explicit shim contract. The first shim migration plan keeps old imports temporary and allowlisted, rewrites lower-risk tool/test consumers, requires a stale old-import static check, and does not retire `validation` or `meta` exceptions during the first apply.

MOVE-BULK-00-PLAN note: global migration planning may group all remaining bad roots, but it remains no-apply until a later gate authorizes exact scope. Batch A is the first gate-ready subset because it contains only docs/evidence/archive material. Batches with identity, authority, runtime, active imports, ABI, or build sensitivity must be gated and may apply safe subsets while deferring unsafe paths. `MOVE-BULK-00-PLAN` does not authorize moves, rewrites, shims, map application, exception retirement, or feature work.

MOVE-BULK-00-GATE note: the global gate authorizes only `MOVE-BULK-01-APPLY-DOCS-ARCHIVE` for Batch A. Apply must use safe-subset behavior and must defer any Batch A item that shows unexpected active-current references. Batches B-G require later gates, and Batch H remains blocked until prior apply/proof tasks complete.

MOVE-BULK-01-APPLY note: safe-subset apply is mandatory in practice, not just in planning. The first Batch A apply moved 26 files with zero exact old-path references and skipped 283 files that still had active/current references. Do not move skipped docs/evidence/archive candidates until a later task explicitly authorizes the required reference rewrites or proves the references historical.

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

<!-- MOVE-ROUTER-00 -->

## MOVE-ROUTER-00 Router Rule

MOVE-ROUTER-00 replaces the remaining deferred B-G micro-plan sequence with a
deterministic dry-run router. This is still no-apply.

Router apply discipline:

1. Generate the route table from `git ls-files`.
2. Route known files to canonical ownership roots.
3. Route unknown or ambiguous files to `archive/quarantine/<root>/`.
4. Report target collisions as blockers.
5. Apply no moves until `MOVE-ROUTER-01` explicitly authorizes the subset.
6. Rewrite references, imports, CMake, and validators only in later repair/apply
   tasks.
7. Retire bad-root exceptions only after tracked roots are empty and proof passes.

Current dry-run summary:

- Bad-root tracked files: 1,765.
- Routed files: 1,765.
- Quarantine routes: 71.
- Target collisions: 0.
- Skipped/impossible routes: 0.
- Next recommended task: `MOVE-ROUTER-01 - Apply Deterministic Bad-Root Router Safe Subset`.

<!-- MOVE-ROUTER-01 -->

## MOVE-ROUTER-01 Apply Rule

MOVE-ROUTER-01 applied the dry-run route table with `git mv` and did not perform
semantic repair.

- Bad-root tracked files before: 1,765.
- Bad-root tracked files after: 0.
- Semantic moves: 1,694.
- Quarantine moves: 71.
- Skipped moves: 0.
- Target collisions: 0.
- Empty-root exceptions retired: 23.

The next task must repair references/imports/build/projection proof rather than
undoing the structural migration.

<!-- RESTRUCTURE-REPAIR-00 -->

## RESTRUCTURE-REPAIR-00 Repair Rule

Safe repair may fix stale paths, stale test fixtures, deterministic proof metadata, and current-status evidence. It must not force deferred root moves, refresh frozen contract hashes, extend expired overrides, accept replay hash drift, or retire layout exceptions unless the root is empty and the exception plan permits it.

RESTRUCTURE-REPAIR-00 confirmed that 23 formerly bad roots still require deferred owner-specific remediation. The next root cleanup task remains `MOVE-BULK-A-SKIPPED-REFERENCE-REFINEMENT`.

<!-- NAME-00 -->

## NAME-00 Naming Canon Rule

Before any further MOVE-BULK refinement or apply task, consume `contracts/repo/naming.contract.toml`.

Naming canon effects:

- do not route moved files through `src/`, `source/`, `sources/`, `code/`, `impl/`, `common/`, `shared/`, or `misc` buckets;
- use singular names for code, service, runtime, and contract-category ownership planes;
- use plural names for authored content, products, tools, docs, tests, and artifact collections;
- keep contract, pack, profile, bundle, release, product, and ABI identity values stable across future path moves;
- treat planned internal renames as future reviewed work, not as implicit MOVE-BULK authorization.

NAME-00 does not authorize moves, rewrites, shims, exception retirement, or feature work.

NAME-00 redo note: the naming canon was refreshed after MOVE-SCRIPT-00 at `148a9adf95bb678da16784434221c568f7bb96cb`. The current no-apply evidence records 1,765 tracked files under former bad roots, 1,593 route candidates, 172 skipped/deferred files, 0 target collisions, and 0 naming-law blockers. Future root recycling must use this current posture without treating it as apply authorization.

<!-- MOVE-SCRIPT-00 -->

## MOVE-SCRIPT-00 Router Rule

Before re-gating deferred MOVE-BULK B-G cleanup, consume `tools/migration/route_bad_roots.py`, `tools/migration/bad_root_routing_rules.json`, and the `.aide/reports/MOVE-SCRIPT-00-*` evidence.

MOVE-SCRIPT-00 is a dry-run planning task only:

- it scans tracked files with `git ls-files`;
- it emits deterministic route candidates, skipped/deferred ledgers, root summaries, and batch summaries;
- it refuses collisions, ambiguous targets, active Python/import-sensitive packages without rewrite or shim plans, identity-sensitive routes without clear ownership, authority-sensitive docs-only routes, ABI/build-sensitive ambiguity, normative `specs/reality` material, and forbidden target segments;
- it does not move, delete, rename, rewrite, shim, apply maps, or retire layout exceptions.

Current dry-run snapshot:

- tracked files under former bad roots: 1,765.
- route candidates: 1,593.
- skipped/deferred files: 172.
- target collisions: 0.
- next recommended task: `MOVE-BULK-BG-REFINEMENT-00 - Re-Gate Deferred B-G Cleanup`.

<!-- MOVE-ROUTER-02 -->

## MOVE-ROUTER-02 Repair Rule

MOVE-ROUTER-02 preserves the MOVE-ROUTER-01 physical cleanup and closes as a
partial repair boundary.

- tracked files under former bad roots: 0.
- active path replacements recorded: 33,316.
- import replacements recorded: 76.
- temporary runtime shim packages created: 3.
- CMake configure: PASS.
- broader TestX: FAIL, 140 of 344 lanes failed.

The next root-recycling action is not another broad move. It is
`MOVE-ROUTER-02R - Finish Registry, Ruleset, Import, and Test Path Repair After Routing`.

## CANON-SPINE-NEW Result

CANON-SPINE-NEW completed the source-spine cleanup layer after bad-root routing.

- Former bad roots remain empty in tracked source.
- `runtime/shell/` is the canonical shell/app/appshell/appcore owner.
- Workbench modules live under `apps/workbench/module/`.
- Root generated/local outputs remain untracked.
- Strict layout/root validators and AIDE pass.

The next root-recycling action is boundary and full-proof repair:
`CANON-SPINE-BOUNDARY-01 - Repair Remaining Boundary Imports and Full Proof`.
