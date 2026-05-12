# Root Inventory

Status: PROVISIONAL
Phase: CONVERGE-09
Machine-readable source: `tools/migration/root_inventory.json`

This document explains the generated inventory. It is not authoritative over the JSON artifacts or layout contracts.

## CONVERGE-09 Note

CONVERGE-09 split safe root-level domain implementation packages into `game/domains/`. Root-level domain folders moved in this pass are absent from the present-root inventory and recorded as completed entries in `tools/migration/root_move_map.json`.

No product, runtime, archive, generated-output, schema-root, or content-root moves occurred, and no new domain features were added.

## Summary Counts

- `allowed_file`: 25
- `canonical`: 13
- `generated_or_ephemeral`: 2
- `metadata`: 4
- `transitional_content_or_data_root`: 7
- `transitional_contract_or_schema_root`: 8
- `transitional_release_or_dist_root`: 1
- `transitional_runtime_root`: 3
- `unknown_needs_review`: 10

## Root Entries

| Root | Classification | Ownership surface | Proposed action | Phase | Risk | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `.agentignore` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |
| `.aide` | `metadata` | `metadata` | `retain_metadata` | `none` | `low` | Allowed metadata/config root. |
| `.aide.local.example` | `metadata` | `metadata` | `retain_metadata` | `none` | `low` | Allowed metadata/config root. |
| `.gitattributes` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |
| `.github` | `metadata` | `metadata` | `retain_metadata` | `none` | `low` | Allowed metadata/config root. |
| `.gitignore` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |
| `.vscode` | `metadata` | `metadata` | `retain_metadata` | `none` | `low` | Allowed metadata/config root. |
| `AGENTS.md` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |
| `apps` | `canonical` | `apps` | `keep` | `none` | `low` | Thin product entrypoints and product composition surfaces. |
| `archive` | `canonical` | `archive` | `keep` | `none` | `low` | Historical, superseded, quarantined, generated-evidence, and legacy material retained with provenance. |
| `artifacts` | `generated_or_ephemeral` | `generated` | `ignore_generated` | `review` | `review` | Review before using as authority. |
| `bundles` | `transitional_content_or_data_root` | `content` | `split` | `CONVERGE-09` | `high` | Authored bundles and generated exports require separate handling. |
| `CHANGELOG.md` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |
| `CLAUDE.md` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |
| `cmake` | `canonical` | `cmake` | `keep` | `none` | `low` | CMake modules and build configuration helpers. |
| `CMakeLists.txt` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |
| `CMakePresets.json` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |
| `CODE_CHANGE_JUSTIFICATION.md` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |
| `compat` | `transitional_contract_or_schema_root` | `contracts` | `review` | `CONVERGE-06` | `review` | Root-level compat/ remains mixed implementation and shim code after CONVERGE-06; do not move wholesale into contracts/. |
| `content` | `canonical` | `content` | `keep` | `none` | `low` | Authored packs, profiles, fixtures, datasets, assets, and domain data. |
| `contracts` | `canonical` | `contracts` | `keep` | `none` | `low` | Machine-readable and prose contracts for schemas, registries, protocols, compatibility, stability, replay, ABI, repository, and distribution rules. |
| `CONTRIBUTING.md` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |
| `control` | `transitional_runtime_root` | `runtime` | `split` | `CONVERGE-07` | `high` | Control substrate must preserve process-only mutation boundaries. |
| `core` | `transitional_runtime_root` | `runtime` | `split` | `CONVERGE-07` | `high` | Core is likely mixed; do not move wholesale. |
| `data` | `transitional_content_or_data_root` | `content` | `split` | `CONVERGE-09` | `high` | Data contains registries, content, planning mirrors, and generated evidence; split by authority. |
| `dist` | `generated_or_ephemeral` | `generated` | `ignore_generated` | `review` | `review` | Distribution output is governed by distribution contracts, not source repo layout. |
| `docs` | `canonical` | `docs` | `keep` | `none` | `low` | Human-readable doctrine, guides, audits, and explanatory material. |
| `DOMINIUM.md` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |
| `engine` | `canonical` | `engine` | `keep` | `none` | `low` | Deterministic Domino substrate and public engine contracts. |
| `game` | `canonical` | `game` | `keep` | `none` | `low` | Dominium rules, domain process semantics, and authoritative game meaning. |
| `governance` | `unknown_needs_review` | `unknown` | `review` | `review` | `review` | Governance mirrors must not compete with AGENTS.md or canon. |
| `GOVERNANCE.md` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |
| `ide` | `unknown_needs_review` | `unknown` | `review` | `review` | `review` | IDE projections may belong under cmake, tools, or generated evidence depending on role. |
| `lib` | `transitional_contract_or_schema_root` | `unknown` | `review` | `CONVERGE-06` | `review` | Do not classify by name alone; inspect ownership first. |
| `libs` | `transitional_contract_or_schema_root` | `unknown` | `review` | `CONVERGE-06` | `review` | Do not classify by name alone; inspect ownership first. |
| `LICENSE.md` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |
| `locks` | `transitional_contract_or_schema_root` | `contracts` | `review` | `CONVERGE-06` | `review` | Root-level locks/ remains review because it contains concrete deterministic pack lock artifacts, not only lockfile schemas. |
| `meta` | `unknown_needs_review` | `unknown` | `review` | `review` | `review` | Meta surfaces require ownership review. |
| `meta_extensions_engine.py` | `unknown_needs_review` | `unknown` | `review` | `review` | `review` | No matching root classification in layout contract. |
| `modding` | `transitional_content_or_data_root` | `content` | `split` | `CONVERGE-09` | `high` | Modding may include content, contracts, and docs. |
| `MODDING.md` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |
| `models` | `transitional_content_or_data_root` | `content` | `move` | `CONVERGE-09` | `medium` | Model data should be distinguished from generated or runtime state. |
| `net` | `transitional_runtime_root` | `runtime` | `split` | `CONVERGE-07` | `high` | Root-level net/ remains mixed after CONVERGE-07 because it contains transport, anti-cheat, SRZ, and server-authoritative policy code; do not move wholesale. |
| `numeric_discipline.py` | `unknown_needs_review` | `unknown` | `review` | `review` | `review` | No matching root classification in layout contract. |
| `packs` | `transitional_content_or_data_root` | `content` | `split` | `CONVERGE-09` | `high` | Current runtime pack substrate; pack ownership split remains review-sensitive. |
| `performance` | `unknown_needs_review` | `unknown` | `review` | `review` | `review` | Performance tooling and evidence should stay tool/evidence scoped. |
| `profiles` | `transitional_content_or_data_root` | `content` | `move` | `CONVERGE-09` | `medium` | Profile data belongs under content unless runtime-store evidence proves otherwise. |
| `README.md` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |
| `release` | `canonical` | `release` | `keep` | `none` | `low` | Release definitions, package recipes, matrices, signing metadata, and release policy inputs. |
| `repo` | `transitional_contract_or_schema_root` | `contracts` | `split` | `CONVERGE-06` | `high` | Do not add new authority here; split later into contracts/repo, docs/repo, or tools/migration. |
| `runtime` | `canonical` | `runtime` | `keep` | `none` | `medium` | Runtime host, AppShell, platform, render, input, audio, network, storage, diagnostics, and UI adapters. Present canonical target root; inspect contents before treating adjacent... |
| `safety` | `transitional_contract_or_schema_root` | `contracts` | `split` | `CONVERGE-06` | `high` | Safety policy belongs under contracts or docs depending on authority. |
| `scripts` | `canonical` | `scripts` | `keep` | `none` | `low` | Developer workflow scripts and repository automation entrypoints. |
| `security` | `transitional_contract_or_schema_root` | `contracts` | `split` | `CONVERGE-06` | `high` | Security and trust surfaces are protected and review-sensitive. |
| `SECURITY.md` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |
| `sitecustomize.py` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |
| `specs` | `transitional_contract_or_schema_root` | `contracts` | `split` | `CONVERGE-06` | `high` | Normative specs must retain authority; reality specs remain canonical over data projections. |
| `templates` | `transitional_content_or_data_root` | `content` | `split` | `CONVERGE-09` | `high` | Templates may be authored content, contracts, or generated inputs. |
| `tests` | `canonical` | `tests` | `keep` | `none` | `low` | Test suites, determinism checks, fixtures, and verification evidence inputs. |
| `tool_ui_bind.cmd` | `unknown_needs_review` | `unknown` | `review` | `review` | `review` | No matching root classification in layout contract. |
| `tool_ui_doc_annotate.cmd` | `unknown_needs_review` | `unknown` | `review` | `review` | `review` | No matching root classification in layout contract. |
| `tool_ui_validate.cmd` | `unknown_needs_review` | `unknown` | `review` | `review` | `review` | No matching root classification in layout contract. |
| `tools` | `canonical` | `tools` | `keep` | `none` | `low` | Developer, validation, migration, CI, code generation, review, and audit tools. |
| `updates` | `transitional_release_or_dist_root` | `release` | `split` | `review` | `high` | Update metadata belongs to release/control-plane ownership after review. |
| `validation` | `unknown_needs_review` | `unknown` | `review` | `review` | `review` | Validation tooling belongs under tools unless it is contract law. |
| `VERSION_CLIENT` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |
| `VERSION_ENGINE` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |
| `VERSION_GAME` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |
| `VERSION_LAUNCHER` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |
| `VERSION_SERVER` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |
| `VERSION_SETUP` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |
| `VERSION_SUITE` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |
| `VERSION_TOOLS` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |

## Unknown Or Review Roots

- `artifacts`: `generated_or_ephemeral`, target `generated evidence or release artifact review`, risk `review`. Review before using as authority.
- `compat`: `transitional_contract_or_schema_root`, target `contracts/compatibility_plus_runtime_review`, risk `review`. Root-level compat/ remains mixed implementation and shim code after CONVERGE-06; do not move wholesale into contracts/.
- `dist`: `generated_or_ephemeral`, target `generated distribution output; future distribution contract review`, risk `review`. Distribution output is governed by distribution contracts, not source repo layout.
- `governance`: `unknown_needs_review`, target `docs/governance`, risk `review`. Governance mirrors must not compete with AGENTS.md or canon.
- `ide`: `unknown_needs_review`, target `cmake_or_tools_review`, risk `review`. IDE projections may belong under cmake, tools, or generated evidence depending on role.
- `lib`: `transitional_contract_or_schema_root`, target `review`, risk `review`. Do not classify by name alone; inspect ownership first.
- `libs`: `transitional_contract_or_schema_root`, target `review`, risk `review`. Do not classify by name alone; inspect ownership first.
- `locks`: `transitional_contract_or_schema_root`, target `contracts/locks_or_store_locks_review`, risk `review`. Root-level locks/ remains review because it contains concrete deterministic pack lock artifacts, not only lockfile schemas.
- `meta`: `unknown_needs_review`, target `review`, risk `review`. Meta surfaces require ownership review.
- `meta_extensions_engine.py`: `unknown_needs_review`, target `review`, risk `review`. No matching root classification in layout contract.
- `numeric_discipline.py`: `unknown_needs_review`, target `review`, risk `review`. No matching root classification in layout contract.
- `performance`: `unknown_needs_review`, target `tools/performance`, risk `review`. Performance tooling and evidence should stay tool/evidence scoped.
- `tool_ui_bind.cmd`: `unknown_needs_review`, target `review`, risk `review`. No matching root classification in layout contract.
- `tool_ui_doc_annotate.cmd`: `unknown_needs_review`, target `review`, risk `review`. No matching root classification in layout contract.
- `tool_ui_validate.cmd`: `unknown_needs_review`, target `review`, risk `review`. No matching root classification in layout contract.
- `validation`: `unknown_needs_review`, target `tools/validation`, risk `review`. Validation tooling belongs under tools unless it is contract law.

## Split-Required Domain Roots

- `astro`: `split` -> `game/domains/astronomy`; status `completed`; phase `CONVERGE-09`.
- `chem`: `split` -> `game/domains/chemistry`; status `completed`; phase `CONVERGE-09`.
- `diegetics`: `split` -> `game/domains/diegetics`; status `completed`; phase `CONVERGE-09`.
- `electric`: `split` -> `game/domains/electricity`; status `completed`; phase `CONVERGE-09`.
- `embodiment`: `split` -> `game/domains/embodiment`; status `completed`; phase `CONVERGE-09`.
- `epistemics`: `split` -> `game/domains/epistemics`; status `completed`; phase `CONVERGE-09`.
- `field`: `split` -> `game/domains/fields/from_root_field`; status `completed`; phase `CONVERGE-09`.
- `fields`: `split` -> `game/domains/fields`; status `completed`; phase `CONVERGE-09`.
- `fluid`: `split` -> `game/domains/fluids`; status `completed`; phase `CONVERGE-09`.
- `geo`: `split` -> `game/domains/geology`; status `completed`; phase `CONVERGE-09`.
- `infrastructure`: `split` -> `game/domains/infrastructure`; status `completed`; phase `CONVERGE-09`.
- `inspection`: `split` -> `game/domains/inspection`; status `completed`; phase `CONVERGE-09`.
- `interaction`: `split` -> `game/domains/interaction`; status `completed`; phase `CONVERGE-09`.
- `interior`: `split` -> `game/domains/interior`; status `completed`; phase `CONVERGE-09`.
- `logic`: `split` -> `game/domains/logic`; status `completed`; phase `CONVERGE-09`.
- `logistics`: `split` -> `game/domains/logistics`; status `completed`; phase `CONVERGE-09`.
- `machines`: `split` -> `game/domains/machines`; status `completed`; phase `CONVERGE-09`.
- `materials`: `split` -> `game/domains/materials`; status `completed`; phase `CONVERGE-09`.
- `mechanics`: `split` -> `game/domains/mechanics`; status `completed`; phase `CONVERGE-09`.
- `mobility`: `split` -> `game/domains/mobility`; status `completed`; phase `CONVERGE-09`.
- `physics`: `split` -> `game/domains/physics`; status `completed`; phase `CONVERGE-09`.
- `pollution`: `split` -> `game/domains/pollution`; status `completed`; phase `CONVERGE-09`.
- `process`: `split` -> `game/domains/processes`; status `completed`; phase `CONVERGE-09`.
- `reality`: `split` -> `game/domains/reality`; status `completed`; phase `CONVERGE-09`.
- `signals`: `split` -> `game/domains/signals`; status `completed`; phase `CONVERGE-09`.
- `system`: `split` -> `game/domains/systems`; status `completed`; phase `CONVERGE-09`.
- `thermal`: `split` -> `game/domains/thermal`; status `completed`; phase `CONVERGE-09`.
- `universe`: `split` -> `game/domains/universe`; status `completed`; phase `CONVERGE-09`.
- `worldgen`: `split` -> `game/domains/worldgen`; status `completed`; phase `CONVERGE-09`.

## Generated Or Ephemeral Roots

- `artifacts`: Review before using as authority.
- `dist`: Distribution output is governed by distribution contracts, not source repo layout.

## Metadata And Root Files

- `.agentignore`: `allowed_file`
- `.aide`: `metadata`
- `.aide.local.example`: `metadata`
- `.gitattributes`: `allowed_file`
- `.github`: `metadata`
- `.gitignore`: `allowed_file`
- `.vscode`: `metadata`
- `AGENTS.md`: `allowed_file`
- `CHANGELOG.md`: `allowed_file`
- `CLAUDE.md`: `allowed_file`
- `CMakeLists.txt`: `allowed_file`
- `CMakePresets.json`: `allowed_file`
- `CODE_CHANGE_JUSTIFICATION.md`: `allowed_file`
- `CONTRIBUTING.md`: `allowed_file`
- `DOMINIUM.md`: `allowed_file`
- `GOVERNANCE.md`: `allowed_file`
- `LICENSE.md`: `allowed_file`
- `MODDING.md`: `allowed_file`
- `README.md`: `allowed_file`
- `SECURITY.md`: `allowed_file`
- `sitecustomize.py`: `allowed_file`
- `VERSION_CLIENT`: `allowed_file`
- `VERSION_ENGINE`: `allowed_file`
- `VERSION_GAME`: `allowed_file`
- `VERSION_LAUNCHER`: `allowed_file`
- `VERSION_SERVER`: `allowed_file`
- `VERSION_SETUP`: `allowed_file`
- `VERSION_SUITE`: `allowed_file`
- `VERSION_TOOLS`: `allowed_file`

## CONVERGE-10 Enforcement Note

CONVERGE-10 adds strict layout validation with explicit exceptions. The machine-readable inventory remains `tools/migration/root_inventory.json`; this document is explanatory.

Current enforcement summary after CONVERGE-10:

- Canonical roots: 13
- Metadata roots: 4
- Allowed root files: 25
- Generated or ephemeral roots: 2
- Active layout exceptions: 32
- Unexcepted strict violations: 0

Strict mode now passes only because every remaining generated, transitional, missing, unknown, or review root has an active entry in `contracts/repo/layout_exceptions.toml`.

Active exceptions cover the missing canonical `external/`, generated roots (`artifacts/`, `dist/`), review roots such as `compat/`, `control/`, `core/`, `data/`, `locks/`, `meta/`, `net/`, `packs/`, `repo/`, `security/`, `specs/`, and `updates/`, and root-level compatibility or review files such as `meta_extensions_engine.py`, `numeric_discipline.py`, and `tool_ui_*.cmd`.

New root-level entries must either match the contracts and allowlist or add a specific, bounded exception. No broad wildcard exception exists.

## CONVERGE-12 Final Inventory Status

Machine-readable source: `tools/migration/root_inventory.json`.

Final CONVERGE-12 inventory status:

- Inventory status: complete
- Canonical roots: 13
- Metadata roots: 4
- Allowed root files: 25
- Generated or ephemeral roots: 2
- Active layout exceptions: 34
- Unexcepted strict violations: 0

All active exceptions now carry `POST-CONVERGE` retirement metadata. Final audit: `docs/repo/audits/CONVERGE_12_FINAL_AUDIT.md`.

## POST-CONVERGE-01 Generated Output Cleanup

POST-CONVERGE-01 removed ignored, untracked generated/cache roots `.xstack_cache/`, `build/`, and `out/` and refreshed `tools/migration/root_inventory.json`.

Current generated/output exception state:

- Active generated/output exceptions: `artifacts/` and `dist/`.
- Retired generated/output exceptions: `.xstack_cache/`, `build/`, and `out/`.
- Active layout exception count: 34.
- Unexcepted strict violations: 0.

## POST-CONVERGE-02 Wrapper / Tooling / Governance Cleanup

POST-CONVERGE-02 removed the unused root package marker and moved quarantined labs documentation from `labs/README.md` to `archive/historical/labs/README.md`.

Current wrapper/tooling/governance inventory state:

- Active layout exception count: 32.
- Unknown/review root count: 10.
- Retired root/file exceptions: `__init__.py` and `labs`.
- Remaining root compatibility shims: `tool_ui_bind.cmd`, `tool_ui_doc_annotate.cmd`, and `tool_ui_validate.cmd`.
- Remaining protected review roots/files: `governance`, `ide`, `meta`, `meta_extensions_engine.py`, `numeric_discipline.py`, `performance`, and `validation`.
- Unexcepted strict violations: 0.

## POST-CONVERGE-03 Content / Pack / Profile / Bundle Cleanup

POST-CONVERGE-03 inspected `data`, `packs`, `profiles`, `bundles`, `modding`, `models`, and `templates` and kept them active as narrowed exceptions.

Current content/package/profile/bundle inventory state:

- Active layout exception count: 32.
- Retired in this task: none.
- `data/` remains mixed across registries, authored pack declarations, world/domain data, planning mirrors, generated evidence, baselines, release/runtime data, and XStack metadata.
- `packs/` remains the runtime pack substrate; `data/packs/` remains scoped authored pack content/declaration material and residual-quarantined for single-root convergence.
- `profiles/` and `bundles/` remain identity-sensitive because profile and bundle IDs, hashes, lock semantics, and release/XStack references are live.
- `modding/` and `models/` remain active implementation packages, not content-only roots.
- `templates/` remains active because protected specs/reality and XStack/AIDE contract references still point at it.
- Unexcepted strict violations: 0.
