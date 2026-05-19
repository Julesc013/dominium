Status: DERIVED
Last Reviewed: 2026-05-20
Supersedes: none
Superseded By: none
Stability: provisional
Task: PACK-AUTHORITY-01

# PACK-AUTHORITY-01 Audit

## Scope

Resolve the active tracked authority split between `contracts/package/packs/`
and `content/packs/` without changing pack IDs, manifest IDs, content hashes,
lock identity, or compatibility semantics. This pass does not perform content
pack taxonomy normalization, schema taxonomy cleanup, app thinning, Workbench
naming, tools folding, docs folding, or feature work.

Starting commit: `6c3f7340f66147b128a66d61d3f2390a27dc4445`

Branch: `main`

Preflight:

- `git status --short --branch`: clean, `main...origin/main`
- `git rev-parse --abbrev-ref HEAD`: `main`
- `git rev-parse HEAD`: `6c3f7340f66147b128a66d61d3f2390a27dc4445`
- Runtime-name, game-rule, and engine-include cleanup are treated as landed or
  out of scope for this task.
- The active tracked tree, not live GitHub or stale generated maps, is the
  source of truth.

## Pack Roots Inspected

- `contracts/package/`
- `contracts/package/packs/`
- `content/packs/`
- `tests/fixtures/package/`
- `archive/generated/`
- `archive/historical/`
- `tools/migration/canon_spine_new.py`
- `tools/validators/repo/check_path_terms.py`
- `contracts/MANIFEST.md`

## Inventory Result

Tracked files under `contracts/package/packs/`:

- `contracts/package/packs/README.md`

Direct children of `contracts/package/packs/` in tracked source:

- `README.md`

Direct children of `content/packs/`:

- `blueprint/`
- `core/`
- `derived/`
- `domain/`
- `example/`
- `experience/`
- `law/`
- `official/`
- `reality/`
- `representation/`
- `spec/`
- `tool/`
- `worldgen/`

Tracked authored pack payload count under `content/packs/`: `628` files.

## Overlapping Pack IDs

No overlapping active tracked pack IDs were found between `content/packs/` and
`contracts/package/packs/` because `contracts/package/packs/` contains no
tracked pack directories or pack manifests.

## Classification

`contracts/package/packs/README.md` is retained as a guard-only contract note.
It is not a pack manifest, authored payload, fixture, generated artifact, lock,
compatibility matrix, or historical copy.

No files under `contracts/package/packs/` required movement.

## Routing Decisions

- Authored pack payloads and pack-local manifests are authoritative under
  `content/packs/`.
- Package law, schemas, policies, lock formats, compatibility contracts, and
  package verification contracts belong under `contracts/package/`,
  `contracts/schema/package/`, or another precise contract owner.
- Test-only package fixtures belong under `tests/fixtures/package/` or the
  existing package fixture taxonomy.
- Generated package artifacts and evidence belong under `archive/generated/`
  or the owning generated-output root.
- `contracts/package/packs/` survives only as
  `contracts/package/packs/README.md`.

## Files Moved

None in this pass. There were no tracked payload files under
`contracts/package/packs/` to move.

## Files Intentionally Retained Under Contracts/Package

- `contracts/package/packs/README.md`: finite guard stating that authored pack
  payloads belong under `content/packs/`, fixtures under test fixture roots, and
  generated package artifacts outside this guard path.
- `contracts/package/locks/pack_lock.mvp_default.json`: lock artifact retained
  under package contract/lock authority; not part of the authored payload split.
- `contracts/package/bundles/README.md`: package bundle contract note; not an
  authored pack payload.

## Stale References Updated

- `contracts/package/packs/README.md` now explicitly routes fixtures and
  generated package artifacts away from the guard path.
- `contracts/MANIFEST.md` now identifies `contracts/package/` as the package
  contract class and marks `contracts/package/packs/README.md` as guard-only.
- `tools/migration/canon_spine_new.py` no longer routes old
  `contracts/packs/` material to `contracts/package/packs/`; it routes package
  contract/law material to `contracts/package/`.
- `tools/validators/repo/check_path_terms.py` now reports any tracked path
  under `contracts/package/packs/` other than the guard README as a blocker.

## Generated/Historical References Skipped

Generated AIDE context, root-classification, and report files still contain
historical generated mentions of old `contracts/package/packs/<pack_id>` paths.
They were not hand-edited. Their refresh belongs to the generated-current path
map/proof tooling pass, not this package authority source repair.

Historical docs and generated reports under audit/report roots were not updated
unless they describe current package authority.

## Identity Preservation

No pack payloads or manifests were moved in this pass. Therefore pack IDs,
manifest IDs, content hashes, lock identity, compatibility semantics, and
capability fields were not mutated.

## Validation Results

- `git diff --check`: PASS.
- `python .aide/scripts/aide_lite.py validate`: PASS with existing warnings for
  missing review packet review ref and stale repo-map source snapshot hash.
- `python tools/validators/repo/check_bad_root_absence.py --strict --json`:
  PASS.
- `python tools/validators/repo/check_no_src_source_dirs.py --json`:
  PASS_WITH_WARNINGS; findings are info-level archive/historical `src` and
  `source` paths.
- `python tools/validators/repo/check_path_terms.py --strict --json
  --max-findings 20`: PASS_WITH_WARNINGS; no blockers.
- Synthetic guard regression check for
  `contracts/package/packs/org.example.pack/pack_manifest.json`: BLOCKED with
  `pack_authority_guard`.
- `python tools/validators/repo/check_forbidden_root_names.py --json`:
  PASS_WITH_WARNINGS; no blockers.
- `python tools/validators/repo/check_directory_naming.py --json
  --max-findings 20`: PASS_WITH_WARNINGS; no blockers.
- `python tools/validators/repo/check_file_naming.py --json --max-findings 20`:
  PASS_WITH_WARNINGS; no blockers.
- `python scripts/verify_build_target_boundaries.py`: PASS.
- `python scripts/verify_includes_sanity.py`: PASS.
- `python scripts/verify_docs_sanity.py`: PASS.
- `python scripts/verify_ui_shell_purity.py`: PASS.
- `python scripts/verify_abi_boundaries.py`: PASS.
- `python tools/build/validate_build_contract.py`: PASS.
- `python -m py_compile tools/migration/canon_spine_new.py
  tools/validators/repo/check_path_terms.py`: PASS.
- `python tools/pack/pack_validate.py --repo-root . --pack-root
  content/packs/core/org.dominium.core.units --format json`: PASS; deprecated
  shim warning emitted before the JSON success payload.
- `python tests/invariant/test_pack_duplicate_pack_id_refusal.py --repo-root .`:
  PASS.
- `cmake --preset verify`: PASS.
- `cmake --build --preset verify --target ALL_BUILD`: PASS. Existing
  duplicate-symbol linker warnings remain in `domino_engine` for graphics/system
  stub symbols; this task did not introduce new link targets or symbols.
- `ctest --preset verify -L smoke --output-on-failure --timeout 300`: PASS,
  57/57.
- `ctest --preset verify -R "(tools_pack_validate|test_pack_duplicate_pack_id_refusal|pack|package)"
  --output-on-failure --timeout 300`: FAIL, 12/22 failed. Failures are stale
  proof/test expectations for old `data/packs`, missing old package schemas, and
  missing old tool wrapper paths; direct active pack validation passed against
  `content/packs/core/org.dominium.core.units`.
- `python scripts/ci/check_repox_rules.py`: FAIL on pre-existing broad RepoX
  issues such as missing `data/registries/*`, missing `data/packs`, stale
  `contracts/schemas/*` expectations, docs status debt, process/runtime guard
  debt, and dist artifact expectations. These are recorded for the later
  RepoX/TestX canonical path repair task.
- `python tools/release/dist/tool_verify_distribution.py --help`: FAIL due
  `ModuleNotFoundError: No module named 'tools'`.
- `python -m tools.release.dist.tool_verify_distribution --help`: FAIL due
  `ModuleNotFoundError: No module named 'tools.dist'`.
- `python -m tools.package.distribution.pkg_verify_all --help`: FAIL due
  `ModuleNotFoundError: No module named 'dompkg_lib'`; direct script help for
  `tools/package/distribution/pkg_verify_all.py` succeeds. This is existing
  distribution-tool import debt.
- `ctest --preset verify --output-on-failure --timeout 300`: FAIL, 390/495
  passed and 105 failed. Failure families are pre-existing stale canonical path
  and proof debt: old `data/world`, `data/registries`, `data/packs`,
  `contracts/schemas`, `game/rules`, `libs/appcore`, `docs/app`, `docs/ui`, and
  missing XStack tool wrapper expectations, plus unrelated invariant debt.
  No failure showed a new active authored pack payload under
  `contracts/package/packs/`.

## Remaining Follow-Up Work

- Regenerate or repair stale generated-current AIDE/RepoX/TestX path maps that
  still mention old `contracts/package/packs/<pack_id>` payload paths.
- Broader stale `data/packs` and historical pack-path proof expectations remain
  out of scope for this task unless a current package authority validator treats
  them as active `contracts/package/packs` payloads.
