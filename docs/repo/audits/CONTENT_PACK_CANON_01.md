Status: DERIVED
Last Reviewed: 2026-05-20
Supersedes: none
Superseded By: none
Stability: provisional
Task: CONTENT-PACK-CANON-01

# CONTENT-PACK-CANON-01 Audit

## Starting State

- Starting commit: `bfcdcf94ace1f859657e53fb52988160e488b0de`
- Branch: `main`
- Initial worktree: clean, with branch ahead of `origin/main` by prior local canonical commits.
- Source of truth: active tracked tree. Live GitHub, historical docs, and generated snapshots were not used as authority.
- Scope: normalize active authored content layout under `content/`, especially `content/packs/` and `content/domains/`.

## Content Roots Inspected

- `content/`
- `content/packs/`
- `content/domains/`
- `content/defaults/`
- `content/profiles/`
- `content/bundles/`
- `content/templates/`
- `content/examples/`
- `content/fixtures/`
- `tools/package/distribution/`
- `tools/pack/`
- `tools/coverage/`
- `tools/inspect/`
- active package/content tests under `tests/contentlib/`, `tests/data_1/`, `tests/contract/`, `tests/distribution/`, `tests/signal/`, and `tests/tools/`

## Chosen Pack Layout

`content/packs/<category>/<pack_id>/`

Allowed categories are the finite set documented in `content/packs/README.md` and enforced by `tools/validators/repo/check_content_layout.py`:

- `blueprint`
- `core`
- `derived`
- `domain`
- `example`
- `experience`
- `law`
- `official`
- `reality`
- `representation`
- `spec`
- `tool`
- `worldgen`

The active tracked tree no longer has flat `content/packs/org.dominium.*` pack roots and no longer has retired active categories such as `content/packs/blueprints`, `content/packs/specs`, or `content/packs/physics`.

## Pack And Category Routes

Previously landed route decisions remain correct in the active tree:

- `content/packs/blueprints/` -> `content/packs/blueprint/`
- `content/packs/specs/` -> `content/packs/spec/`
- `content/packs/physics/physics.default.realistic/` -> `content/packs/domain/physics.default.realistic/`
- `content/packs/system_templates/base/` -> `content/packs/core/system_templates.base/`
- Flat `org.dominium.base.*` and `org.dominium.core.*` packs -> `content/packs/core/`
- Flat `org.dominium.examples.*` packs -> `content/packs/example/`
- Flat `org.dominium.realities.*`, `org.dominium.earth.srtm`, and `org.dominium.sol.spice` packs -> `content/packs/reality/`
- Flat `org.dominium.worldgen.*` packs -> `content/packs/worldgen/`
- Remaining flat domain-like `org.dominium.*` packs -> `content/packs/domain/`

This pass added `content/packs/blueprint/blueprints.default.m1/pack.json` because the directory already contained authored blueprint payloads but had no pack manifest. The payload files were not changed.

## Content Domain Routes

Previously landed route decisions remain correct in the active tree:

- `content/domains/game/core/astro/sol/` -> `content/domains/astronomy/sol/`
- `content/domains/game/core/cosmo/` -> `content/domains/cosmology/`
- `content/domains/game/core/mechanics/` -> `content/domains/mechanics/`
- `content/domains/game/core/README.md` -> `content/domains/README.game-core-migration.md`
- `content/domains/worldgen/real/*/content/*` -> `content/domains/worldgen/real/*/*`

Active tracked inventory now has no `content/domains/game/core/` and no `content/domains/**/content/` tautology.

## Files Moved Or Added

- No tracked files required a new `git mv` in this pass; prior route moves were already present in the active tree.
- Added `content/packs/blueprint/blueprints.default.m1/pack.json` as the missing manifest for an existing authored blueprint pack.
- Added `tools/validators/repo/check_content_layout.py`.
- Added `tests/contentlib/content_layout_validator_tests.py`.
- Repointed `tools/ci/validate_sol_data.py`, `tools/ci/validate_earth_data.py`, and `tools/ci/validate_milky_way_data.py` from retired `data/world/**` paths to canonical `content/domains/worldgen/real/**` data.

## Identity Preservation

- No existing pack payload, pack ID, manifest ID, content hash, lock identity, compatibility field, capability field, or trust sidecar was mutated.
- The new blueprint manifest uses the existing directory identity `blueprints.default.m1` and existing payload IDs from the files already under that pack.
- Existing pack-internal `content/` payload folders were not rewritten; changing those would be a package-format migration beyond this task.

## References Updated

- Active tests now resolve pack roots under `content/packs/<category>/<pack_id>/` instead of `data/packs/<pack_id>/`.
- Package discovery defaults now use `content/packs`.
- Pack validation, coverage inspection, refusal explanation, capability-gating migration, AuditX pack analyzers, and RepoX process registry collection now use `content/packs`.
- Legacy `data/packs/<pack_id>` path shim resolution now falls through to the matching canonical category pack under `content/packs`.
- Current content/tool docs now point examples at `content/packs`.
- `tools/assetc/tool_assetc.c` now defaults authored asset input/output to `content/assets/...` rather than old `data/...` surfaces.
- Smoke-test harness references for ControlX/PerformX were updated to their active `tools/xstack/**` paths so the required smoke CTest lane could run without old tool-root assumptions.

## Generated And Historical References Skipped

- `docs/content/archive/**` retains historical `data/packs` references.
- Planning and generated evidence references to `content/domains/game/core` were not rewritten because they describe prior structural state or generated/historical proof.
- Compatibility shim and legacy-path tests intentionally keep `data/packs` literals as migration/redirect fixtures.
- Generated audit outputs under `docs/audit/**`, planning generated data, and architecture registry snapshots were not hand-edited.

## Validator Update

- Existing `tools/validators/repo/check_path_terms.py` already blocks retired active content wrappers and retired pack category names.
- New `tools/validators/repo/check_content_layout.py` enforces:
  - finite `content/packs/<category>/<pack_id>/` categories
  - no flat `content/packs/<pack_id>` active layout
  - pack leaves must have `pack.json`, `pack.toml`, `pack.manifest`, or `pack_manifest.json`
  - no `content/domains/game/core`
  - no `content/domains/**/content` tautology
- `tests/contentlib/content_layout_validator_tests.py` covers valid category layout, invalid flat layout, missing manifest, retired `game/core`, and nested domain `content/` wrappers.

## Validation Results

Preflight:

- `git status --short`: clean at start.
- `git rev-parse --abbrev-ref HEAD`: `main`.
- `git rev-parse HEAD`: `bfcdcf94ace1f859657e53fb52988160e488b0de`.
- `python .aide/scripts/aide_lite.py validate`: passed with existing warnings about missing review policy reference and stale repo-map source snapshot hash.

Focused content/package proof:

- `python tools/validators/repo/check_content_layout.py --strict --json --max-findings 20`: passed.
- `python tools/ci/validate_sol_data.py --repo-root .`: passed.
- `python tools/ci/validate_earth_data.py --repo-root .`: passed.
- `python tools/ci/validate_milky_way_data.py --repo-root .`: passed.
- Focused Python package/content tests under `tests/contentlib`, `tests/data_1`, `tests/tools`, `tests/app`, `tests/contract`, `tests/distribution`, and `tests/signal`: passed.
- `python tools/package/distribution/pack_discover.py --repo-root . --format json`: passed, found 106 packs including `blueprints.default.m1`.
- `python tools/package/distribution/compat_dry_run.py --repo-root . --require-capability org.dominium.core.units --format json`: passed.
- `python tools/pack/pack_validate.py --pack-root content/packs/core/org.dominium.core.units --repo-root . --format json`: passed.

Repo/proof validators:

- `git diff --check`: passed.
- `python tools/validators/repo/check_bad_root_absence.py --strict --json`: passed.
- `python tools/validators/repo/check_no_src_source_dirs.py --strict --json --max-findings 20`: passed with warnings only, no blockers.
- `python tools/validators/repo/check_forbidden_root_names.py --strict --json --max-findings 20`: passed with warnings only, no blockers.
- `python tools/validators/repo/check_directory_naming.py --strict --json`: passed with warnings only, no blockers.
- `python tools/validators/repo/check_file_naming.py --strict --json`: passed with warnings only, no blockers.
- `python scripts/verify_build_target_boundaries.py`: passed.
- `python scripts/verify_includes_sanity.py`: passed.
- `python scripts/verify_docs_sanity.py`: passed.
- `python scripts/verify_ui_shell_purity.py`: passed.
- `python scripts/verify_abi_boundaries.py`: passed.
- `python tests/schema/schema_reference_integrity_tests.py --repo-root .`: passed.
- `python tests/schema/schema_taxonomy_validator_tests.py --repo-root .`: passed.

Build and CTest:

- `cmake --preset verify`: passed.
- `cmake --build --preset verify --target ALL_BUILD`: passed. Existing duplicate-symbol linker warnings in `domino_engine` remained; this task did not introduce them.
- Focused CTest after repairs:
  `ctest --preset verify -R "dominium_content1_sol_data|dominium_content2_earth_data|dominium_content3_milky_way_data|engine_smoke|client_flow_smoke|distribution_sdk_engine_compile_smoke|distribution_sdk_game_compile_smoke|controlx_smoke|performx_smoke|content_layout|contentlib_pack|data1_pack|tools_pack|pack_resolution|pack_scope|signal_pack|distribution_prealpha" --output-on-failure`
  passed 17/17.
- Final focused CTest rerun after cleaning validation-generated churn:
  `ctest --preset verify -R "dominium_content1_sol_data|dominium_content2_earth_data|dominium_content3_milky_way_data|controlx_smoke|performx_smoke|content_layout|contentlib_pack|data1_pack|tools_pack|pack_resolution|pack_scope|signal_pack|distribution_prealpha" --output-on-failure`
  passed 13/13.
- Full CTest was attempted before the stale worldgen data validators were repaired and failed 67 of 497 tests. The failures were broad pre-existing proof debt outside this content layout task, including stale `data/registries`, `contracts/schemas`, `game/rules`, old tool-root expectations, docs/header debt, process-only mutation checks, and frozen hash drift. The three content data failures from that run were repaired and covered by the focused CTest above.

Known remaining validation caveat:

- `python tests/invariant/invariant_no_raw_paths.py --repo-root .` still fails on pre-existing absolute-path fixture data in `tests/fixtures/audit/baseline_universe_verify.json` and `tests/fixtures/regression/proc_full_baseline.json`; those files were not introduced or modified by this task.

## Remaining Follow-Up Work

- Broader historical/generated path maps still contain old path names and should be handled by the proof-lane repair task when those maps are active.
- Pack-internal `content/` payload roots remain where current pack format uses them; changing that requires a package-format migration task.
