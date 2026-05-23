Status: DERIVED
Last Reviewed: 2026-05-20
Supersedes: none
Superseded By: none
Stability: provisional
Task: SCHEMA-CANON-01

# SCHEMA-CANON-01 Audit

## Scope

Canonicalize active tracked `contracts/schema/` buckets that still encoded old root names, abbreviation-era names, or duplicate singular/plural schema taxonomy. This pass is limited to schema taxonomy, directly stale active path references, and focused validator proof.

Starting commit: `9c2b4a693d49cc9e196b4217eea2b9f050fbe13d`

Branch: `main`

## Schema Buckets Inspected

- `contracts/schema/chem/`
- `contracts/schema/domain/civilization/`
- `contracts/schema/domain/civilization/`
- `contracts/schema/compat/`
- `contracts/schema/control/`
- `contracts/schema/core/`
- `contracts/schema/diag/`
- `contracts/schema/electric/`
- `contracts/schema/fab/`
- `contracts/schema/domain/fluids/`
- `contracts/schema/domain/geology/`
- `contracts/schema/lib/`
- `contracts/schema/material/`
- `contracts/schema/materials/`
- `contracts/schema/models/`
- `contracts/schema/mods/`
- `contracts/schema/runtime/network/`
- `contracts/schema/packs/`
- `contracts/schema/physical/`
- `contracts/schema/runtime/render/`
- `contracts/schema/specs/`
- `contracts/schema/tech/`
- `contracts/schema/technology/`
- `contracts/schema/tool/`
- `contracts/schema/tools/`
- `contracts/schema/validator/`

The previously moved old buckets `chem`, `civ`, `civilisation`, `compat`, `control`, `core`, `diag`, `fluid`, `geo`, `lib`, `material`, `materials`, `models`, `mods`, `net`, `packs`, `render`, `specs`, `tools`, and `validator` had no active tracked files at the start of this continuation. The active tracked exceptions found by this pass were `electric` and `technology`.

## Routing Decisions

- `contracts/schema/electric/` is a domain schema bucket for electrical network and protection schemas; it moved to `contracts/schema/domain/electricity/`.
- `contracts/schema/technology/` is a domain-facing technology specification bucket; it moved to `contracts/schema/domain/technology/`.
- `contracts/schema/tool/` remains the canonical tool schema owner.
- Root `schema/` and `schemas/` aliases now point at `contracts/schema`, not the retired plural `contracts/schemas` spelling.
- RepoX stale schema aliases now route old schema bucket spellings directly to canonical owners, including `domain/chemistry`, `domain/civilization`, `domain/fluids`, `domain/geology`, `domain/electricity`, `domain/technology`, `package`, `runtime/network`, `runtime/render`, `runtime/control`, `runtime/diagnostics`, `tool`, and `validation`.
- Focused CTest exposed active proof paths still using `contracts/schemas` and `tools/compatx`; those were repaired to `contracts/schema` and `tools/xstack/compatx`.
- CompatX registry inputs were routed from retired `data/registries` paths to current `contracts/registry` and `contracts/schema/registry` authorities.

## Schema Identity

Schema bodies, `schema_id` values, `schema_version` values, and semantic schema names were preserved. No `$id` or semantic identity migration was performed. Existing `SCHEMA:` header labels that encode older short schema names were left unchanged, matching the previous schema-canon move policy and avoiding silent schema identity drift.

The active bundle profile registry already encoded bundle optionality in `extensions.optional`; top-level `optional` fields were added with the same boolean values to satisfy the current CompatX registry contract without changing bundle identity or optional/core semantics.

## Files Moved

- `contracts/schema/electric/elec_edge_payload.schema` -> `contracts/schema/domain/electricity/elec_edge_payload.schema`
- `contracts/schema/electric/elec_node_payload.schema` -> `contracts/schema/domain/electricity/elec_node_payload.schema`
- `contracts/schema/electric/fault_state.schema` -> `contracts/schema/domain/electricity/fault_state.schema`
- `contracts/schema/electric/grounding_policy.schema` -> `contracts/schema/domain/electricity/grounding_policy.schema`
- `contracts/schema/electric/protection_device.schema` -> `contracts/schema/domain/electricity/protection_device.schema`
- `contracts/schema/electric/protection_settings.schema` -> `contracts/schema/domain/electricity/protection_settings.schema`
- `contracts/schema/electric/storage_state.schema` -> `contracts/schema/domain/electricity/storage_state.schema`
- `contracts/schema/electric/trip_explanation.schema` -> `contracts/schema/domain/electricity/trip_explanation.schema`
- `contracts/schema/technology/SPEC_TECH_EFFECTS.md` -> `contracts/schema/domain/technology/SPEC_TECH_EFFECTS.md`
- `contracts/schema/technology/SPEC_TECH_PREREQUISITES.md` -> `contracts/schema/domain/technology/SPEC_TECH_PREREQUISITES.md`

All moved tracked files were moved with `git mv`.

## References Updated

- `contracts/repo/layout.contract.toml`
- `contracts/repo/root_allowlist.toml`
- `contracts/registry/bundle_profiles.json`
- `contracts/schema/SCHEMA_GOVERNANCE.md`
- `contracts/schema/SCHEMA_MIGRATION.md`
- `contracts/schema/SCHEMA_VERSIONING.md`
- `docs/repo/MOVE_MAP.md`
- `docs/archive/audit/security/INTEGRITY_MANIFEST.json`
- `scripts/ci/check_repox_rules.py`
- `tests/invariant/process_registry_execution_tests.py`
- `tests/invariant/process_registry_tests.py`
- `tests/schema/CMakeLists.txt`
- `tests/schema/schema_migration_tests.py`
- `tests/schema/schema_reference_integrity_tests.py`
- `tests/schema/schema_taxonomy_validator_tests.py`
- `tests/signal/signal_schema_contract_tests.py`
- `tests/tools/compatx_migration_tests.py`
- `tests/tools/compatx_pack_matrix_tests.py`
- `tests/tools/compatx_save_replay_tests.py`
- `tests/tools/compatx_schema_diff_tests.py`
- `tools/validators/ci/phase6_audit_checks.py`
- `tools/release/dist/dist_tree_common.py`
- `tools/validators/check_repo_layout.py`
- `tools/validators/repo/check_path_terms.py`
- `tools/xstack/compatx/compatx.py`
- `tools/xstack/auditx/analyzers/e107_undeclared_schema_smell.py`

## Validator Update

`tools/validators/repo/check_path_terms.py` now blocks the electric, physical, fabrication, tech, and technology schema root spellings and reports duplicate spelling splits for chemistry, geology, fluids, civilization, materials, and tool schema roots.

The focused validator test `tests/schema/schema_taxonomy_validator_tests.py` covers:

- retired `contracts/schema/geo` fails;
- canonical `contracts/schema/domain/geology` passes;
- old schema paths under `archive/legacy` do not fail active-source validation;
- duplicate retired/canonical geology roots produce `schema_duplicate_spelling`.

## Generated And Historical References Skipped

Stale old schema paths remain in generated or historical audit evidence such as `docs/archive/audit/**`, `.aide/**`, and migration route inventories. They were not hand-edited because they are generated/historical evidence rather than current schema authority.

## Validation Results

- `git status --short --branch`: clean at preflight except branch ahead of origin and generated AIDE task packet modification.
- `python .aide/scripts/aide_lite.py doctor`: PASS.
- `python .aide/scripts/aide_lite.py validate`: PASS with existing AIDE review-packet/repo-map freshness warnings.
- `python .aide/scripts/aide_lite.py pack --task "SCHEMA-CANON-01"`: PASS; generated `.aide/context/latest-task-packet.md`, later reverted before commit.
- `git diff --check`: PASS.
- `git ls-files` for retired active schema buckets: PASS, no tracked files under the retired buckets.
- `python tools/validators/repo/check_path_terms.py --strict --json --max-findings 20`: PASS_WITH_WARNINGS, blocker count 0.
- `python tests/schema/schema_taxonomy_validator_tests.py --repo-root .`: PASS.
- `python tests/schema/schema_migration_tests.py --repo-root .`: PASS.
- `python tests/schema/schema_reference_integrity_tests.py --repo-root .`: PASS.
- `python tests/invariant/process_registry_tests.py --repo-root .`: PASS.
- `python tests/invariant/process_registry_execution_tests.py --repo-root .`: PASS.
- `ctest --preset verify -R "schema|process_registry|compatx" --output-on-failure --timeout 300`: PASS, 16/16.
- `python -m json.tool contracts\registry\bundle_profiles.json`: PASS.
- `python -m json.tool docs\audit\security\INTEGRITY_MANIFEST.json`: PASS.
- `python tools/validators/repo/check_bad_root_absence.py --strict --json`: PASS.
- `python tools/validators/repo/check_no_src_source_dirs.py --json`: PASS_WITH_WARNINGS, blocker count 0; findings are historical archive paths.
- `python tools/validators/repo/check_forbidden_root_names.py --json`: PASS_WITH_WARNINGS, blocker count 0; findings are historical archive paths.
- `python scripts/verify_build_target_boundaries.py`: PASS.
- `python scripts/verify_includes_sanity.py`: PASS.
- `python scripts/verify_docs_sanity.py`: PASS.
- `python scripts/verify_ui_shell_purity.py`: PASS.
- `python scripts/verify_abi_boundaries.py`: PASS.
- `cmake --preset verify`: PASS.
- `cmake --build --preset verify --target ALL_BUILD`: PASS with pre-existing duplicate symbol linker warnings on `domino_engine` stubs.
- `ctest --preset verify -L smoke --output-on-failure --timeout 300`: PASS, 57/57.
- `ctest --preset verify -R "schema|process_registry|compatx|signal_schema_contracts" --output-on-failure --timeout 300`: PASS, 16/16.
- `ctest --preset verify --output-on-failure --timeout 300`: FAIL, 400/496 passed and 96 failed. Failures are broad pre-existing/out-of-scope proof debts including retired `data/` pack and registry expectations, distribution artifact expectations, RepoX/TestX stale path lanes, historical blocker audits, content pack scope checks, and profile bundle stress markers. The schema, process registry, CompatX, and signal schema focused slice passed after this change.

## Remaining Follow-Up Work

- Generated audit and AIDE maps still contain historical old schema paths and should be refreshed only through their owning generators.
- Many older tests and generated proof lanes still reference root `schema/`, plural `schemas/`, or root-level flat schema projection paths. Those are proof-infrastructure debts for REPOX-TESTX-CANON-PATHS-01 unless a current validator treats them as authoritative.
- If schema IDs must eventually align with physical path taxonomy, perform that as an explicit schema identity migration with versioned compatibility review.
