Status: DERIVED
Last Reviewed: 2026-05-20
Supersedes: none
Superseded By: none
Stability: audit

# REPOX-TESTX-CANON-PATHS-01

## Starting Point

- Starting commit: `f0fa0a4c16ebf1c24c90911ea28f32dd9891799c`
- Branch: `main`
- Initial worktree: clean
- Active tracked tree was treated as source of truth; live GitHub and old generated reports were not used as authority.

## Task Scope

Repair stale canonical path expectations in proof infrastructure after the source-spine cleanup. The task did not recreate old roots, did not move authored/source payloads, and did not change semantic IDs, pack IDs, schema IDs, lock IDs, or content hashes.

## Failing Commands Before Changes

Captured before fixes:

- `py -3 .aide/scripts/aide_lite.py validate`: PASS, with existing warnings for missing review-packet ref and stale repo-map source snapshot hash.
- `py -3 .aide/scripts/aide_lite.py selftest`: PASS.
- `py -3 .aide/scripts/aide_lite.py test`: PASS.
- `py -3 .aide/scripts/aide_lite.py roots validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py repo validate`: PASS.
- `python scripts/dev/testx_proof_engine.py --repo-root . --suite testx_fast --dry-run ...`: FAIL with `refuse.invalid_suite_registry` because the default registry was `data/registries/testx_suites.json`.
- `python scripts/ci/check_repox_rules.py --repo-root . --profile STRICT ...`: FAIL. In-scope stale findings included old docs/contracts display and stale path constants; broad residual failures were also present.
- `python scripts/dev/run_repox.py`: PASS/exit 0, but it did not surface the direct RepoX STRICT failures.
- `python tools/validators/repo/check_bad_root_absence.py --repo-root . --strict`: PASS.
- `python tools/validators/repo/check_no_src_source_dirs.py --repo-root . --strict`: PASS_WITH_WARNINGS, archive/legacy `source` paths classified as historical archive info.
- `python tools/validators/repo/check_forbidden_root_names.py --repo-root . --strict`: PASS_WITH_WARNINGS for finite historical/exception cases.
- `python tools/validators/repo/check_tools_taxonomy.py --repo-root . --strict`: PASS.
- `python tools/validators/repo/check_docs_taxonomy.py --repo-root . --strict`: PASS.
- `python tools/validators/check_root_allowlist.py`: PASS with existing exceptions.
- `python tools/validators/check_repo_layout.py`: PASS with existing exceptions.
- `python scripts/verify_build_target_boundaries.py --repo-root .`: PASS.
- `python scripts/verify_includes_sanity.py --repo-root .`: PASS.
- `python scripts/verify_ui_shell_purity.py --repo-root .`: PASS.
- `python scripts/verify_abi_boundaries.py --repo-root .`: PASS.

Captured outputs were written to ignored temp directories under `%TEMP%` and not committed.

## Stale Path Classes Found

- TestX default registry path: `data/registries/testx_suites.json` -> `contracts/registry/testx_suites.json`.
- TestX default proof output paths: `docs/audit/...` -> `docs/archive/audit/...`.
- RepoX direct path constants still expecting old registry/doc/compat/server roots.
- RepoX canonical alias table lacked several post-canon path mappings used by migration fixtures and current proof maps.
- RepoX negotiation doctrine marker contained mojibaked smart quotes, causing a Windows/UTF-8 false negative against the current doc.
- TestX worldgen/network policy tests and AuditX analyzers still loaded or watched registry authority under `data/registries/`.
- Current generated root maps in `tools/migration/root_inventory.json` and `tools/migration/root_move_map.json` carried the previous head SHA and were refreshed by validator execution.

## Path Maps Updated

Updated `scripts/ci/check_repox_rules.py` canonical aliases for:

- `contracts/registries/` -> `contracts/registry/`
- `contracts/capabilities/` -> `contracts/capability/`
- `contracts/package/packs/` -> `content/packs/`
- `runtime/render/soft/` -> `runtime/render/software/`
- `runtime/render/stub/` -> `runtime/render/null/`
- `runtime/render/client/renderers/` -> `runtime/render/backend/`
- `runtime/shell/commands/` -> `runtime/shell/command/`
- `runtime/shell/ui_backends/` -> `runtime/ui/backend/`
- `runtime/capability/capability/` -> `runtime/capability/core/`
- `runtime/ui/core/` -> `runtime/ui/service/`
- `game/rules/` -> `game/rule/`
- `game/include/dominium/rules/` -> `game/include/dominium/law/`
- `tools/validator/` -> `tools/validators/`
- `tools/validation/` -> `tools/validators/validation/`

Updated RepoX direct checked paths from old roots to current owners:

- `data/registries/*` -> `contracts/registry/*`
- `docs/contracts/*` -> `docs/reference/contracts/*`
- `docs/compat/*` -> `docs/compatibility/*`
- `docs/audit/*` -> `docs/archive/audit/*`
- `compat/capability_negotiation.py` -> `tools/validators/compatibility/capability_negotiation.py`
- `compat/descriptor/*` -> `tools/validators/compatibility/descriptor/*`
- `compat/negotiation/*` -> `tools/validators/compatibility/negotiation/*`
- `apps/server/net/*` -> `runtime/network/server/*`
- `tools/server/*` -> `tools/test/server/*`

Updated `scripts/dev/testx_proof_engine.py` defaults to canonical active paths.

Updated current TestX and AuditX proof references from `data/registries/` to `contracts/registry/` for:

- worldgen module and constraints registries
- network replication policy registry
- anti-cheat policy and module registries
- AuditX schema/capability/domain analyzer watch prefixes and related paths

## Fixtures Updated

- Updated `tests/invariant/testx_manifest_selection_tests.py` to assert the default TestX suite registry is `contracts/registry/testx_suites.json` and that the loader resolves that canonical path.
- Updated focused TestX cases that directly open registry files to use `contracts/registry`.
- No migration fixtures were moved or reclassified in this task.

## Generators Run Or Identified

- AIDE `pack --task "REPOX-TESTX-CANON-PATHS-01"` refreshed `.aide/context/latest-task-packet.md`; this is current AIDE generated context and was retained.
- Root/layout validator execution refreshed `tools/migration/root_inventory.json` and `tools/migration/root_move_map.json` head/timestamp fields; these are current generated path maps and were retained.
- No archive/generated or archive/legacy snapshots were hand-edited.

## Generated/Historical References Skipped

Skipped stale references in:

- `docs/archive/**`
- top-level `archive/**`
- `.aide/reports/**`, `.aide/refactors/**`, `.aide/roots/**`, and similar AIDE historical evidence surfaces
- docs audit records documenting old failures, including CANON_DEBT and previous source-spine audits
- migration tooling whose purpose is to route old paths, such as `tools/migration/canon_spine_new.py`

These were not treated as active current-source blockers unless a validator directly executed them as current proof logic.

## Residual Failures Outside Scope

Direct RepoX STRICT still fails after stale path repair, but the remaining failures are not stale path expectations from this task. Residual classes include:

- missing status headers in historical/current docs
- missing distribution artifacts under `dist/`
- stale identity fingerprint artifact
- process guard/runtime and process-only mutation invariants
- raw Windows path fixtures
- wallclock token in descriptor logic
- official pack compatibility manifest absence
- schema-version reference debt
- frozen tool-version hash mismatches
- worldgen lock/fingerprint drift
- silent-default findings in existing tool/runtime code

## Validation Results

Post-fix focused results:

- `git diff --check`: PASS.
- `python -m py_compile` over all modified Python files: PASS.
- `py -3 .aide/scripts/aide_lite.py validate`: PASS, with existing warnings for missing review-packet ref and stale repo-map source snapshot hash.
- `py -3 .aide/scripts/aide_lite.py selftest`: PASS.
- `py -3 .aide/scripts/aide_lite.py test`: PASS.
- `py -3 .aide/scripts/aide_lite.py roots validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py repo validate`: PASS.
- `python scripts/dev/testx_proof_engine.py --repo-root . --suite testx_fast --dry-run ...`: PASS, loads `contracts/registry/testx_suites.json`.
- `python tools/xstack/testx/tests/test_worldgen_multi_seed_determinism.py --repo-root .`: PASS.
- `python tools/xstack/testx/tests/test_policy_matrix_rules.py --repo-root .`: PASS.
- `python tools/xstack/securex/securex.py integrity-manifest --repo-root . --output docs/archive/audit/security/INTEGRITY_MANIFEST.json`: PASS; regenerated current integrity manifest through the generator.
- `python tools/validators/repo/check_bad_root_absence.py --repo-root . --strict`: PASS.
- `python tools/validators/repo/check_no_src_source_dirs.py --repo-root . --strict`: PASS_WITH_WARNINGS for archive/legacy historical paths.
- `python tools/validators/repo/check_forbidden_root_names.py --repo-root . --strict`: PASS_WITH_WARNINGS for finite archive/material exceptions.
- `python tools/validators/repo/check_tools_taxonomy.py --repo-root . --strict`: PASS.
- `python tools/validators/repo/check_docs_taxonomy.py --repo-root . --strict`: PASS.
- `python tools/validators/check_root_allowlist.py`: PASS with existing transitional-root notes.
- `python tools/validators/check_repo_layout.py`: PASS with existing transitional-root notes.
- `cmake --preset verify`: PASS with existing SDL/PkgConfig warnings.
- `cmake --build --preset verify --target ALL_BUILD`: PASS.
- `ctest --preset verify -R "^(tools_auditx|tools_auditx_changed_only|tools_auditx_hash_stability|test_auditx_canonical_hash_stability|test_auditx_empty_path|test_auditx_arbitrary_cwd)$" --output-on-failure`: PASS, 6/6.
- `ctest --preset verify -R "^(engine_smoke|test_manifest_selection_logic|test_manifest_fallback_when_missing|tools_auditx|tools_auditx_changed_only|tools_auditx_hash_stability)$" --output-on-failure`: PASS, 6/6.
- `python scripts/ci/check_repox_rules.py --repo-root . --profile STRICT ...`: FAIL, but stale TestX registry, old docs/contracts negotiation path, old compat descriptor emitted path, and targeted stale path literals in strict output were repaired. Remaining failures are residual non-path proof debt listed above.
- Full CTest was not run; focused AuditX/TestX/smoke CTest coverage was run.

## Remaining Follow-Up Work

- Refresh or regenerate `.aide/repo/*` and historical AIDE maps with their owning AIDE generators if those maps are promoted to current authority.
- Address direct RepoX STRICT residual debt in focused tasks for docs status headers, dist artifact proof, process invariants, schema-version references, tool hash locks, worldgen lock drift, and silent defaults.
- Decide whether `scripts/dev/run_repox.py` should propagate the same strict lane as direct `check_repox_rules.py`; it currently exits 0 while direct STRICT reports failures.
