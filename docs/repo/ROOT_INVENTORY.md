# Root Inventory

Status: PROVISIONAL
Phase: CONVERGE-08
Machine-readable source: `tools/migration/root_inventory.json`

This document explains the generated inventory. The JSON inventory and layout contracts remain the machine-readable planning sources.

CONVERGE-08 updated this inventory after moving root-level `client/`, `server/`, `setup/`, and `launcher/` under `apps/`. No domain split occurred.

## Summary Counts

- `allowed_file`: 25
- `canonical`: 12
- `generated_or_ephemeral`: 4
- `metadata`: 4
- `split_required_domain_root`: 29
- `transitional_content_or_data_root`: 7
- `transitional_contract_or_schema_root`: 8
- `transitional_release_or_dist_root`: 1
- `transitional_runtime_root`: 3
- `unknown_needs_review`: 12

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
| `__init__.py` | `unknown_needs_review` | `unknown` | `review` | `review` | `review` | No matching root classification in layout contract. |
| `AGENTS.md` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |
| `apps` | `canonical` | `apps` | `keep` | `none` | `low` | Thin product entrypoints and product composition surfaces. |
| `archive` | `canonical` | `archive` | `keep` | `none` | `low` | Historical, superseded, quarantined, generated-evidence, and legacy material retained with provenance. |
| `artifacts` | `generated_or_ephemeral` | `generated` | `ignore_generated` | `review` | `review` | Review before using as authority. |
| `astro` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/astro; contracts/registries/astro; game/domains/astro; content/domain-data/astro; docs/domains/astro; tests/determinism/astro; tests/fixtur... |
| `build` | `generated_or_ephemeral` | `generated` | `ignore_generated` | `review` | `review` | Must not be treated as source repository ownership. |
| `bundles` | `transitional_content_or_data_root` | `content` | `split` | `CONVERGE-09` | `high` | Authored bundles and generated exports require separate handling. |
| `CHANGELOG.md` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |
| `chem` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/chem; contracts/registries/chem; game/domains/chem; content/domain-data/chem; docs/domains/chem; tests/determinism/chem; tests/fixtures/chem |
| `CLAUDE.md` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |
| `cmake` | `canonical` | `cmake` | `keep` | `none` | `low` | CMake modules and build configuration helpers. |
| `CMakeLists.txt` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |
| `CMakePresets.json` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |
| `CODE_CHANGE_JUSTIFICATION.md` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |
| `compat` | `transitional_contract_or_schema_root` | `contracts` | `review` | `CONVERGE-06` | `review` | Root-level compat/ remains mixed implementation and shim code after CONVERGE-06; do not move wholesale into contracts/. |
| `contracts` | `canonical` | `contracts` | `keep` | `none` | `low` | Machine-readable and prose contracts for schemas, registries, protocols, compatibility, stability, replay, ABI, repository, and distribution rules. |
| `CONTRIBUTING.md` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |
| `control` | `transitional_runtime_root` | `runtime` | `split` | `CONVERGE-07` | `high` | Control substrate must preserve process-only mutation boundaries. |
| `core` | `transitional_runtime_root` | `runtime` | `split` | `CONVERGE-07` | `high` | Core is likely mixed; do not move wholesale. |
| `data` | `transitional_content_or_data_root` | `content` | `split` | `CONVERGE-09` | `high` | Data contains registries, content, planning mirrors, and generated evidence; split by authority. |
| `diegetics` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/diegetics; contracts/registries/diegetics; game/domains/diegetics; content/domain-data/diegetics; docs/domains/diegetics; tests/determinism... |
| `dist` | `generated_or_ephemeral` | `generated` | `ignore_generated` | `review` | `review` | Distribution output is governed by distribution contracts, not source repo layout. |
| `docs` | `canonical` | `docs` | `keep` | `none` | `low` | Human-readable doctrine, guides, audits, and explanatory material. |
| `DOMINIUM.md` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |
| `electric` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/electric; contracts/registries/electric; game/domains/electric; content/domain-data/electric; docs/domains/electric; tests/determinism/elec... |
| `embodiment` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/embodiment; contracts/registries/embodiment; game/domains/embodiment; content/domain-data/embodiment; docs/domains/embodiment; tests/determ... |
| `engine` | `canonical` | `engine` | `keep` | `none` | `low` | Deterministic Domino substrate and public engine contracts. |
| `epistemics` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/epistemics; contracts/registries/epistemics; game/domains/epistemics; content/domain-data/epistemics; docs/domains/epistemics; tests/determ... |
| `field` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/field; contracts/registries/field; game/domains/field; content/domain-data/field; docs/domains/field; tests/determinism/field; tests/fixtur... |
| `fields` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/fields; contracts/registries/fields; game/domains/fields; content/domain-data/fields; docs/domains/fields; tests/determinism/fields; tests/... |
| `fluid` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/fluid; contracts/registries/fluid; game/domains/fluid; content/domain-data/fluid; docs/domains/fluid; tests/determinism/fluid; tests/fixtur... |
| `game` | `canonical` | `game` | `keep` | `none` | `low` | Dominium rules, domain process semantics, and authoritative game meaning. |
| `geo` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/geo; contracts/registries/geo; game/domains/geo; content/domain-data/geo; docs/domains/geo; tests/determinism/geo; tests/fixtures/geo |
| `governance` | `unknown_needs_review` | `unknown` | `review` | `review` | `review` | Governance mirrors must not compete with AGENTS.md or canon. |
| `GOVERNANCE.md` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |
| `ide` | `unknown_needs_review` | `unknown` | `review` | `review` | `review` | IDE projections may belong under cmake, tools, or generated evidence depending on role. |
| `infrastructure` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/infrastructure; contracts/registries/infrastructure; game/domains/infrastructure; content/domain-data/infrastructure; docs/domains/infrastr... |
| `inspection` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/inspection; contracts/registries/inspection; game/domains/inspection; content/domain-data/inspection; docs/domains/inspection; tests/determ... |
| `interaction` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/interaction; contracts/registries/interaction; game/domains/interaction; content/domain-data/interaction; docs/domains/interaction; tests/d... |
| `interior` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/interior; contracts/registries/interior; game/domains/interior; content/domain-data/interior; docs/domains/interior; tests/determinism/inte... |
| `labs` | `unknown_needs_review` | `unknown` | `review` | `review` | `review` | Experimental material requires review before binding. |
| `lib` | `transitional_contract_or_schema_root` | `unknown` | `review` | `CONVERGE-06` | `review` | Do not classify by name alone; inspect ownership first. |
| `libs` | `transitional_contract_or_schema_root` | `unknown` | `review` | `CONVERGE-06` | `review` | Do not classify by name alone; inspect ownership first. |
| `LICENSE.md` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |
| `locks` | `transitional_contract_or_schema_root` | `contracts` | `review` | `CONVERGE-06` | `review` | Root-level locks/ remains review because it contains concrete deterministic pack lock artifacts, not only lockfile schemas. |
| `logic` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/logic; contracts/registries/logic; game/domains/logic; content/domain-data/logic; docs/domains/logic; tests/determinism/logic; tests/fixtur... |
| `logistics` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/logistics; contracts/registries/logistics; game/domains/logistics; content/domain-data/logistics; docs/domains/logistics; tests/determinism... |
| `machines` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/machines; contracts/registries/machines; game/domains/machines; content/domain-data/machines; docs/domains/machines; tests/determinism/mach... |
| `materials` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/materials; contracts/registries/materials; game/domains/materials; content/domain-data/materials; docs/domains/materials; tests/determinism... |
| `mechanics` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/mechanics; contracts/registries/mechanics; game/domains/mechanics; content/domain-data/mechanics; docs/domains/mechanics; tests/determinism... |
| `meta` | `unknown_needs_review` | `unknown` | `review` | `review` | `review` | Meta surfaces require ownership review. |
| `meta_extensions_engine.py` | `unknown_needs_review` | `unknown` | `review` | `review` | `review` | No matching root classification in layout contract. |
| `mobility` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/mobility; contracts/registries/mobility; game/domains/mobility; content/domain-data/mobility; docs/domains/mobility; tests/determinism/mobi... |
| `modding` | `transitional_content_or_data_root` | `content` | `split` | `CONVERGE-09` | `high` | Modding may include content, contracts, and docs. |
| `MODDING.md` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |
| `models` | `transitional_content_or_data_root` | `content` | `move` | `CONVERGE-09` | `medium` | Model data should be distinguished from generated or runtime state. |
| `net` | `transitional_runtime_root` | `runtime` | `split` | `CONVERGE-07` | `high` | Root-level net/ remains mixed after CONVERGE-07 because it contains transport, anti-cheat, SRZ, and server-authoritative policy code; do not move wholesale. |
| `numeric_discipline.py` | `unknown_needs_review` | `unknown` | `review` | `review` | `review` | No matching root classification in layout contract. |
| `out` | `generated_or_ephemeral` | `generated` | `ignore_generated` | `review` | `review` | Must not be treated as source repository ownership. |
| `packs` | `transitional_content_or_data_root` | `content` | `split` | `CONVERGE-09` | `high` | Current runtime pack substrate; pack ownership split remains review-sensitive. |
| `performance` | `unknown_needs_review` | `unknown` | `review` | `review` | `review` | Performance tooling and evidence should stay tool/evidence scoped. |
| `physics` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/physics; contracts/registries/physics; game/domains/physics; content/domain-data/physics; docs/domains/physics; tests/determinism/physics; ... |
| `pollution` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/pollution; contracts/registries/pollution; game/domains/pollution; content/domain-data/pollution; docs/domains/pollution; tests/determinism... |
| `process` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/process; contracts/registries/process; game/domains/process; content/domain-data/process; docs/domains/process; tests/determinism/process; ... |
| `profiles` | `transitional_content_or_data_root` | `content` | `move` | `CONVERGE-09` | `medium` | Profile data belongs under content unless runtime-store evidence proves otherwise. |
| `README.md` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |
| `reality` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/reality; contracts/registries/reality; game/domains/reality; content/domain-data/reality; docs/domains/reality; tests/determinism/reality; ... |
| `release` | `canonical` | `release` | `keep` | `none` | `low` | Release definitions, package recipes, matrices, signing metadata, and release policy inputs. |
| `repo` | `transitional_contract_or_schema_root` | `contracts` | `split` | `CONVERGE-06` | `high` | Do not add new authority here; split later into contracts/repo, docs/repo, or tools/migration. |
| `runtime` | `canonical` | `runtime` | `keep` | `none` | `medium` | Runtime host, AppShell, platform, render, input, audio, network, storage, diagnostics, and UI adapters. Present canonical target root; inspect contents befor... |
| `safety` | `transitional_contract_or_schema_root` | `contracts` | `split` | `CONVERGE-06` | `high` | Safety policy belongs under contracts or docs depending on authority. |
| `scripts` | `canonical` | `scripts` | `keep` | `none` | `low` | Developer workflow scripts and repository automation entrypoints. |
| `security` | `transitional_contract_or_schema_root` | `contracts` | `split` | `CONVERGE-06` | `high` | Security and trust surfaces are protected and review-sensitive. |
| `SECURITY.md` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |
| `signals` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/signals; contracts/registries/signals; game/domains/signals; content/domain-data/signals; docs/domains/signals; tests/determinism/signals; ... |
| `sitecustomize.py` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |
| `specs` | `transitional_contract_or_schema_root` | `contracts` | `split` | `CONVERGE-06` | `high` | Normative specs must retain authority; reality specs remain canonical over data projections. |
| `system` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/system; contracts/registries/system; game/domains/system; content/domain-data/system; docs/domains/system; tests/determinism/system; tests/... |
| `templates` | `transitional_content_or_data_root` | `content` | `split` | `CONVERGE-09` | `high` | Templates may be authored content, contracts, or generated inputs. |
| `tests` | `canonical` | `tests` | `keep` | `none` | `low` | Test suites, determinism checks, fixtures, and verification evidence inputs. |
| `thermal` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/thermal; contracts/registries/thermal; game/domains/thermal; content/domain-data/thermal; docs/domains/thermal; tests/determinism/thermal; ... |
| `tool_ui_bind.cmd` | `unknown_needs_review` | `unknown` | `review` | `review` | `review` | No matching root classification in layout contract. |
| `tool_ui_doc_annotate.cmd` | `unknown_needs_review` | `unknown` | `review` | `review` | `review` | No matching root classification in layout contract. |
| `tool_ui_validate.cmd` | `unknown_needs_review` | `unknown` | `review` | `review` | `review` | No matching root classification in layout contract. |
| `tools` | `canonical` | `tools` | `keep` | `none` | `low` | Developer, validation, migration, CI, code generation, review, and audit tools. |
| `universe` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/universe; contracts/registries/universe; game/domains/universe; content/domain-data/universe; docs/domains/universe; tests/determinism/univ... |
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
| `worldgen` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/worldgen; contracts/registries/worldgen; game/domains/worldgen; content/domain-data/worldgen; docs/domains/worldgen; tests/determinism/worl... |

## Unknown Or Review Roots

- `__init__.py`: unknown_needs_review, risk `review`.
- `artifacts`: generated_or_ephemeral, risk `review`.
- `build`: generated_or_ephemeral, risk `review`.
- `compat`: transitional_contract_or_schema_root, risk `review`.
- `dist`: generated_or_ephemeral, risk `review`.
- `governance`: unknown_needs_review, risk `review`.
- `ide`: unknown_needs_review, risk `review`.
- `labs`: unknown_needs_review, risk `review`.
- `lib`: transitional_contract_or_schema_root, risk `review`.
- `libs`: transitional_contract_or_schema_root, risk `review`.
- `locks`: transitional_contract_or_schema_root, risk `review`.
- `meta`: unknown_needs_review, risk `review`.
- `meta_extensions_engine.py`: unknown_needs_review, risk `review`.
- `numeric_discipline.py`: unknown_needs_review, risk `review`.
- `out`: generated_or_ephemeral, risk `review`.
- `performance`: unknown_needs_review, risk `review`.
- `tool_ui_bind.cmd`: unknown_needs_review, risk `review`.
- `tool_ui_doc_annotate.cmd`: unknown_needs_review, risk `review`.
- `tool_ui_validate.cmd`: unknown_needs_review, risk `review`.
- `validation`: unknown_needs_review, risk `review`.

## Split-Required Roots

- `astro` -> contracts/game/content/docs/tests split
- `bundles` -> content_or_exports_review
- `chem` -> contracts/game/content/docs/tests split
- `compat` -> contracts/compatibility_plus_runtime_review
- `control` -> runtime/control
- `core` -> runtime/core_or_game_domain_review
- `data` -> content_or_runtime_store_review
- `diegetics` -> contracts/game/content/docs/tests split
- `electric` -> contracts/game/content/docs/tests split
- `embodiment` -> contracts/game/content/docs/tests split
- `epistemics` -> contracts/game/content/docs/tests split
- `field` -> contracts/game/content/docs/tests split
- `fields` -> contracts/game/content/docs/tests split
- `fluid` -> contracts/game/content/docs/tests split
- `geo` -> contracts/game/content/docs/tests split
- `infrastructure` -> contracts/game/content/docs/tests split
- `inspection` -> contracts/game/content/docs/tests split
- `interaction` -> contracts/game/content/docs/tests split
- `interior` -> contracts/game/content/docs/tests split
- `locks` -> contracts/locks_or_store_locks_review
- `logic` -> contracts/game/content/docs/tests split
- `logistics` -> contracts/game/content/docs/tests split
- `machines` -> contracts/game/content/docs/tests split
- `materials` -> contracts/game/content/docs/tests split
- `mechanics` -> contracts/game/content/docs/tests split
- `mobility` -> contracts/game/content/docs/tests split
- `modding` -> content/modding
- `net` -> runtime/network
- `packs` -> content/packs
- `physics` -> contracts/game/content/docs/tests split
- `pollution` -> contracts/game/content/docs/tests split
- `process` -> contracts/game/content/docs/tests split
- `reality` -> contracts/game/content/docs/tests split
- `repo` -> split_to_contracts_docs_tools
- `safety` -> contracts/safety
- `security` -> contracts/security
- `signals` -> contracts/game/content/docs/tests split
- `specs` -> contracts/specs
- `system` -> contracts/game/content/docs/tests split
- `templates` -> content/templates
- `thermal` -> contracts/game/content/docs/tests split
- `universe` -> contracts/game/content/docs/tests split
- `updates` -> release_or_ops_review
- `worldgen` -> contracts/game/content/docs/tests split

## Generated Or Ephemeral Roots

- `artifacts`: generated evidence or release artifact review
- `build`: generated build output
- `dist`: generated distribution output; future distribution contract review
- `out`: generated build output

## Metadata And Root Files

- `.agentignore`: allowed_file
- `.aide`: metadata
- `.aide.local.example`: metadata
- `.gitattributes`: allowed_file
- `.github`: metadata
- `.gitignore`: allowed_file
- `.vscode`: metadata
- `AGENTS.md`: allowed_file
- `CHANGELOG.md`: allowed_file
- `CLAUDE.md`: allowed_file
- `CMakeLists.txt`: allowed_file
- `CMakePresets.json`: allowed_file
- `CODE_CHANGE_JUSTIFICATION.md`: allowed_file
- `CONTRIBUTING.md`: allowed_file
- `DOMINIUM.md`: allowed_file
- `GOVERNANCE.md`: allowed_file
- `LICENSE.md`: allowed_file
- `MODDING.md`: allowed_file
- `README.md`: allowed_file
- `SECURITY.md`: allowed_file
- `sitecustomize.py`: allowed_file
- `VERSION_CLIENT`: allowed_file
- `VERSION_ENGINE`: allowed_file
- `VERSION_GAME`: allowed_file
- `VERSION_LAUNCHER`: allowed_file
- `VERSION_SERVER`: allowed_file
- `VERSION_SETUP`: allowed_file
- `VERSION_SUITE`: allowed_file
- `VERSION_TOOLS`: allowed_file

No moves are performed by this document. CONVERGE-08 performed only product-entrypoint root moves already recorded in Git and in the move map.
