Status: DERIVED
Last Reviewed: 2026-05-18
Supersedes: none
Superseded By: none

# Post-Restructure Proof

Latest proof state: PARTIAL after `MOVE-SCRIPT-00`, `POST-RESTRUCTURE-REPAIR-SEMANTIC-LINTS`, `TEST-PERF-01`, and NAME-00 naming-law follow-up.

## PUBLIC-SURFACE-REGISTRY-01 Proof Note

PUBLIC-SURFACE-REGISTRY-01 adds a provisional public surface registry and
validator.

- registry: `contracts/public_surface/public_surface.contract.toml`
- validator: `python tools/validators/repo/check_public_surface.py --repo-root . --strict`
- initial surfaces: 20.
- stable surfaces: 2, limited to repo layout and root allowlist contracts.
- fast strict: PASS, 30/30 commands, 299.828 seconds.
- unproven headers, schemas, package formats, release surfaces, and Workbench
  modules remain provisional or internal.

Feature implementation and DOE-00 remain blocked until Foundation Lock closes.
Next task: `API-ABI-CANON-01`.

## FAST-STRICT-TEST-TIER-01 Proof Note

FAST-STRICT-TEST-TIER-01 adds the normal development gate:

- `fast_strict` = T0 + T1 + T2.
- command: `python tools/test/run_fast_strict.py --repo-root .`
- latest result: PASS, 30/30 commands, 332.828 seconds.
- T3 product/projection proof remains task-dependent.
- T4 full/release proof still owns full CTest and known broad debt.

Feature implementation and DOE-00 remain blocked until Foundation Lock closes.
Next task: `PUBLIC-SURFACE-REGISTRY-01`.

## Passing Proof Surfaces

- AIDE doctor/validate/test/selftest/tools/roots/repo.
- Strict layout/root/distribution/component validators.
- Supplemental docs/build/UI/ABI checks.
- Focused RepoX.
- Smoke CTest.
- Fast CTest label.
- Semantic lint CTest lanes.
- AuditX slow shard.
- Native configure and build-only `ALL_BUILD`.
- Product boot matrix strict smoke.
- Portable projection strict validation.
- Internal pilot release strict validation.
- Frozen contract hash guard.
- Override policy tests.
- Replay hash invariance.

## Remaining Blockers

- Full CTest is not green.
- 23 formerly bad roots remain under active exceptions with 1,765 tracked files in the current `git ls-files` dry-run router inventory.
- MOVE-SCRIPT-00 produced 1,593 route candidates, 172 skipped/deferred files, and 0 target collisions without applying moves.
- AuditX CTest wall-time is now partitioned into explicit `audit`/`auditx`/`slow`/`nightly` shards with 1200 second timeout.
- Large file-quality ledger storage policy remains unresolved.
- Naming conflicts are classified by NAME-00, but no naming migration has been applied.

## Rerun Commands

```powershell
py -3 .aide/scripts/aide_lite.py doctor
py -3 .aide/scripts/aide_lite.py validate
py -3 .aide/scripts/aide_lite.py test
py -3 .aide/scripts/aide_lite.py selftest
py -3 .aide/scripts/aide_lite.py tools validate
py -3 .aide/scripts/aide_lite.py roots validate
py -3 .aide/scripts/aide_lite.py repo validate
python tools/validators/check_repo_layout.py --repo-root . --strict
python tools/validators/check_root_allowlist.py --repo-root . --strict
python tools/validators/check_distribution_layout.py --repo-root . --strict
python tools/validators/check_component_matrices.py --repo-root . --strict
python tools/validators/repo/check_no_src_source_dirs.py --repo-root .
python tools/validators/repo/check_path_terms.py --repo-root .
python tools/validators/repo/check_directory_naming.py --repo-root .
python tools/validators/repo/check_file_naming.py --repo-root .
python tools/migration/route_bad_roots.py --repo-root . --dry-run --rules tools/migration/bad_root_routing_rules.json --json-out .aide/reports/MOVE-SCRIPT-00-routing-preview.json --md-out .aide/reports/MOVE-SCRIPT-00-routing-preview.md --skipped-out .aide/reports/MOVE-SCRIPT-00-skipped-ledger.json --root-summary-out .aide/reports/MOVE-SCRIPT-00-root-summary.json --batch-plan-out .aide/reports/MOVE-SCRIPT-00-batch-plan.json --fail-on-collision
ctest --preset verify -R inv_repox_rules --output-on-failure --timeout 300
ctest --preset verify -R "slice0_hardcoded_ids|slice1_hardcoded_constants" --output-on-failure --timeout 300
ctest --preset verify -L smoke --output-on-failure --timeout 300
ctest --preset verify -L fast --output-on-failure --timeout 300
ctest --preset verify -L audit --output-on-failure --timeout 1200
ctest --preset verify -L slow --output-on-failure --timeout 1200
cmake --preset verify
cmake --build --preset verify --target ALL_BUILD
python tools/validators/check_product_boot_matrix.py --repo-root . --json --strict --run-smoke --timeout 30
python tools/validators/check_portable_projection.py --repo-root . --projection-root .dominium.local/projections/post-converge-12/v0.0.0-post-converge-12/win64/dominium --json --strict
python tools/validators/check_internal_pilot_release.py --repo-root . --release-root .dominium.local/releases/internal-pilot-0 --json --strict
```

## Readiness

DOE-00 is not authorized. Feature implementation remains blocked.

Next task: `MOVE-BULK-BG-REFINEMENT-00 - Re-Gate Deferred B-G Cleanup`.

## Semantic Lint Proof Note

POST-RESTRUCTURE-REPAIR-SEMANTIC-LINTS reproduced 1,104 hardcoded identifier/constant findings and classified every finding before allowing it. The focused lanes now pass through exact-match allowlist entries keyed by test, file, line, validator message, and source-line hash. No broad suppressions were added.

## NAME-00 Naming Proof Note

NAME-00 locks naming law and produces warning-only conflict evidence. It does not make current excepted bad roots clean, and it does not authorize `runtime/appshell -> runtime/shell`, `game/domains -> game/domain`, or contract-category singularization. Those are planned future migrations requiring reviewed scope.

NAME-00 redo at `148a9adf95bb678da16784434221c568f7bb96cb` refreshes the evidence after MOVE-SCRIPT-00:

- NAME-00 blockers: 0.
- no `src`/`source`/`sources` directory findings: 106 total, 13 warnings, 0 blockers.
- forbidden path-term findings: 1,450 total, 78 warnings, 0 blockers.
- directory naming findings: 418 total, 39 warnings, 0 blockers.
- file naming findings: 5,361 total, 4,307 warnings, 0 blockers.
- language ownership finding classes: 4 warnings, 0 blockers.

The redo did not move, delete, rename, rewrite, shim, retire exceptions, or alter behavior. Feature work and DOE-00 remain blocked.

## MOVE-SCRIPT-00 Routing Proof Note

MOVE-SCRIPT-00 added a deterministic dry-run router and rule file for the 23 former bad roots. It scans tracked files through `git ls-files`, produces sorted route and skipped ledgers, detects target collisions, and emits batch plans for the deferred MOVE-BULK B-G cleanup. The task did not move, delete, rename, rewrite, shim, or retire exceptions.

The router result is `PASS_WITH_WARNINGS`: 1,593 route candidates are available for later gate review, and 172 files remain deferred for import, identity, authority, ABI/build, or naming-risk reasons.

## MOVE-ROUTER-00 Routing Proof Note

MOVE-ROUTER-00 supersedes the MOVE-SCRIPT skipped/deferred posture as the
active routing path. The router now routes every tracked file under former bad
roots: known files to canonical owners and unknown or ambiguous files to
`archive/quarantine/<root>/`.

Current dry-run result:

- Bad-root tracked files: 1,765.
- Routed files: 1,765.
- Known canonical routes: 1,694.
- Quarantine routes: 71.
- Target collisions: 0.
- Skipped/impossible routes: 0.
- Moves, deletes, renames, rewrites, shims, and exception retirements: 0.

Feature work and DOE-00 remain blocked. Next structural task:
`MOVE-ROUTER-01 - Apply Deterministic Bad-Root Router Safe Subset`.

## MOVE-ROUTER-01 Apply Proof Note

MOVE-ROUTER-01 physically moved every tracked file under the configured former
bad roots.

- Bad-root tracked files before: 1,765.
- Bad-root tracked files after: 0.
- Files moved: 1,765.
- Semantic moves: 1,694.
- Quarantine moves: 71.
- Skipped moves: 0.
- Target collisions: 0.
- Active root exceptions retired: 23.

This is not full recovery proof. Reference/import/build repair remains assigned
to `MOVE-ROUTER-02`, and feature work plus DOE-00 remain blocked.

## MOVE-ROUTER-02 Repair Proof Note

MOVE-ROUTER-02 closed as PARTIAL. It repaired the first active path/import/build
layer after MOVE-ROUTER-01 while preserving the routed root cleanup.

- Bad-root tracked files after repair: 0.
- Exact path replacements recorded: 33,316.
- Import replacements recorded: 76.
- Runtime control shim packages created: 3.
- CMake configure: PASS.
- Build: PARTIAL; 57/57 integrated fast/smoke tests passed before broader TestX failed.
- Broader TestX: FAIL, 140 of 344 lanes failed.
- Strict repo/root layout validators: PASS at this boundary.

This is not final proof. Remaining blockers are assigned to
`MOVE-ROUTER-02R - Finish Registry, Ruleset, Import, and Test Path Repair After Routing`.

## CANON-SPINE-NEW Proof Note

CANON-SPINE-NEW completed the structural second-level source-spine cleanup after
MOVE-ROUTER-02.

- Former bad roots remain empty: 0 tracked files.
- Root-level generated/local roots remain untracked.
- AIDE doctor/validate/test/selftest/tools/roots/repo: PASS.
- Strict repo/root/distribution/component validators: PASS.
- Smoke CTest: PASS.
- CMake configure: PASS.
- Boundary validation: not green; remaining warnings are documented in
  `.aide/reports/CANON-SPINE-NEW-blockers.md`.

This is not final green proof. Feature work and DOE-00 remain blocked until the
boundary repair and full proof pass.
