# Root Inventory

Status: PROVISIONAL
Phase: CONVERGE-07
Machine-readable source: `tools/migration/root_inventory.json`

This document explains the generated inventory. The JSON inventory and layout contracts remain the machine-readable planning sources.

CONVERGE-07 updated this inventory after moving root-level `app/`, `appshell/`, `ui/`, and `diag/` under `runtime/`. No product or domain moves occurred.

## Summary Counts

- `allowed_file`: 25
- `canonical`: 11
- `generated_or_ephemeral`: 2
- `metadata`: 4
- `split_required_domain_root`: 29
- `transitional_content_or_data_root`: 7
- `transitional_contract_or_schema_root`: 8
- `transitional_product_root`: 4
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
| `archive` | `canonical` | `archive` | `keep` | `none` | `low` | Historical, superseded, quarantined, generated-evidence, and legacy material retained with provenance. |
| `artifacts` | `generated_or_ephemeral` | `generated` | `ignore_generated` | `review` | `review` | Review before using as authority. |
| `astro` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/astro; contracts/registries/astro; game/domains/astro; content/domain-data/astro; docs/domains/astro; tests/determinism... |
| `bundles` | `transitional_content_or_data_root` | `content` | `split` | `CONVERGE-09` | `high` | Authored bundles and generated exports require separate handling. |
| `CHANGELOG.md` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |
| `chem` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/chem; contracts/registries/chem; game/domains/chem; content/domain-data/chem; docs/domains/chem; tests/determinism/chem... |
| `CLAUDE.md` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |
| `client` | `transitional_product_root` | `apps` | `move` | `CONVERGE-08` | `medium` | Only thin product binding should remain under apps. |
| `cmake` | `canonical` | `cmake` | `keep` | `none` | `low` | CMake modules and build configuration helpers. |
| `CMakeLists.txt` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |
| `CMakePresets.json` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |
| `CODE_CHANGE_JUSTIFICATION.md` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |
| `compat` | `transitional_contract_or_schema_root` | `contracts` | `review` | `CONVERGE-06` | `review` | Root-level compat/ remains mixed implementation and shim code after CONVERGE-06; do not move wholesale into contracts/. |
| `contracts` | `canonical` | `contracts` | `keep` | `none` | `low` | Machine-readable and prose contracts for schemas, registries, protocols, compatibility, stability, replay, ABI, repository, and distribut... |
| `CONTRIBUTING.md` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |
| `control` | `transitional_runtime_root` | `runtime` | `split` | `CONVERGE-07` | `high` | Control substrate must preserve process-only mutation boundaries. |
| `core` | `transitional_runtime_root` | `runtime` | `split` | `CONVERGE-07` | `high` | Core is likely mixed; do not move wholesale. |
| `data` | `transitional_content_or_data_root` | `content` | `split` | `CONVERGE-09` | `high` | Data contains registries, content, planning mirrors, and generated evidence; split by authority. |
| `diegetics` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/diegetics; contracts/registries/diegetics; game/domains/diegetics; content/domain-data/diegetics; docs/domains/diegetic... |
| `dist` | `generated_or_ephemeral` | `generated` | `ignore_generated` | `review` | `review` | Distribution output is governed by distribution contracts, not source repo layout. |
| `docs` | `canonical` | `docs` | `keep` | `none` | `low` | Human-readable doctrine, guides, audits, and explanatory material. |
| `DOMINIUM.md` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |
| `electric` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/electric; contracts/registries/electric; game/domains/electric; content/domain-data/electric; docs/domains/electric; te... |
| `embodiment` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/embodiment; contracts/registries/embodiment; game/domains/embodiment; content/domain-data/embodiment; docs/domains/embo... |
| `engine` | `canonical` | `engine` | `keep` | `none` | `low` | Deterministic Domino substrate and public engine contracts. |
| `epistemics` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/epistemics; contracts/registries/epistemics; game/domains/epistemics; content/domain-data/epistemics; docs/domains/epis... |
| `field` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/field; contracts/registries/field; game/domains/field; content/domain-data/field; docs/domains/field; tests/determinism... |
| `fields` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/fields; contracts/registries/fields; game/domains/fields; content/domain-data/fields; docs/domains/fields; tests/determ... |
| `fluid` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/fluid; contracts/registries/fluid; game/domains/fluid; content/domain-data/fluid; docs/domains/fluid; tests/determinism... |
| `game` | `canonical` | `game` | `keep` | `none` | `low` | Dominium rules, domain process semantics, and authoritative game meaning. |
| `geo` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/geo; contracts/registries/geo; game/domains/geo; content/domain-data/geo; docs/domains/geo; tests/determinism/geo; test... |
| `governance` | `unknown_needs_review` | `unknown` | `review` | `review` | `review` | Governance mirrors must not compete with AGENTS.md or canon. |
| `GOVERNANCE.md` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |
| `ide` | `unknown_needs_review` | `unknown` | `review` | `review` | `review` | IDE projections may belong under cmake, tools, or generated evidence depending on role. |
| `infrastructure` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/infrastructure; contracts/registries/infrastructure; game/domains/infrastructure; content/domain-data/infrastructure; d... |
| `inspection` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/inspection; contracts/registries/inspection; game/domains/inspection; content/domain-data/inspection; docs/domains/insp... |
| `interaction` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/interaction; contracts/registries/interaction; game/domains/interaction; content/domain-data/interaction; docs/domains/... |
| `interior` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/interior; contracts/registries/interior; game/domains/interior; content/domain-data/interior; docs/domains/interior; te... |
| `labs` | `unknown_needs_review` | `unknown` | `review` | `review` | `review` | Experimental material requires review before binding. |
| `launcher` | `transitional_product_root` | `apps` | `move` | `CONVERGE-08` | `medium` | Launcher product identity and executable naming must remain stable. |
| `lib` | `transitional_contract_or_schema_root` | `unknown` | `review` | `CONVERGE-06` | `review` | Do not classify by name alone; inspect ownership first. |
| `libs` | `transitional_contract_or_schema_root` | `unknown` | `review` | `CONVERGE-06` | `review` | Do not classify by name alone; inspect ownership first. |
| `LICENSE.md` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |
| `locks` | `transitional_contract_or_schema_root` | `contracts` | `review` | `CONVERGE-06` | `review` | Root-level locks/ remains review because it contains concrete deterministic pack lock artifacts, not only lockfile schemas. |
| `logic` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/logic; contracts/registries/logic; game/domains/logic; content/domain-data/logic; docs/domains/logic; tests/determinism... |
| `logistics` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/logistics; contracts/registries/logistics; game/domains/logistics; content/domain-data/logistics; docs/domains/logistic... |
| `machines` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/machines; contracts/registries/machines; game/domains/machines; content/domain-data/machines; docs/domains/machines; te... |
| `materials` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/materials; contracts/registries/materials; game/domains/materials; content/domain-data/materials; docs/domains/material... |
| `mechanics` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/mechanics; contracts/registries/mechanics; game/domains/mechanics; content/domain-data/mechanics; docs/domains/mechanic... |
| `meta` | `unknown_needs_review` | `unknown` | `review` | `review` | `review` | Meta surfaces require ownership review. |
| `meta_extensions_engine.py` | `unknown_needs_review` | `unknown` | `review` | `review` | `review` | No matching root classification in layout contract. |
| `mobility` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/mobility; contracts/registries/mobility; game/domains/mobility; content/domain-data/mobility; docs/domains/mobility; te... |
| `modding` | `transitional_content_or_data_root` | `content` | `split` | `CONVERGE-09` | `high` | Modding may include content, contracts, and docs. |
| `MODDING.md` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |
| `models` | `transitional_content_or_data_root` | `content` | `move` | `CONVERGE-09` | `medium` | Model data should be distinguished from generated or runtime state. |
| `net` | `transitional_runtime_root` | `runtime` | `split` | `CONVERGE-07` | `high` | Root-level net/ remains mixed after CONVERGE-07 because it contains transport, anti-cheat, SRZ, and server-authoritative policy code; do... |
| `numeric_discipline.py` | `unknown_needs_review` | `unknown` | `review` | `review` | `review` | No matching root classification in layout contract. |
| `packs` | `transitional_content_or_data_root` | `content` | `split` | `CONVERGE-09` | `high` | Current runtime pack substrate; pack ownership split remains review-sensitive. |
| `performance` | `unknown_needs_review` | `unknown` | `review` | `review` | `review` | Performance tooling and evidence should stay tool/evidence scoped. |
| `physics` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/physics; contracts/registries/physics; game/domains/physics; content/domain-data/physics; docs/domains/physics; tests/d... |
| `pollution` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/pollution; contracts/registries/pollution; game/domains/pollution; content/domain-data/pollution; docs/domains/pollutio... |
| `process` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/process; contracts/registries/process; game/domains/process; content/domain-data/process; docs/domains/process; tests/d... |
| `profiles` | `transitional_content_or_data_root` | `content` | `move` | `CONVERGE-09` | `medium` | Profile data belongs under content unless runtime-store evidence proves otherwise. |
| `README.md` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |
| `reality` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/reality; contracts/registries/reality; game/domains/reality; content/domain-data/reality; docs/domains/reality; tests/d... |
| `release` | `canonical` | `release` | `keep` | `none` | `low` | Release definitions, package recipes, matrices, signing metadata, and release policy inputs. |
| `repo` | `transitional_contract_or_schema_root` | `contracts` | `split` | `CONVERGE-06` | `high` | Do not add new authority here; split later into contracts/repo, docs/repo, or tools/migration. |
| `runtime` | `canonical` | `runtime` | `keep` | `none` | `medium` | Runtime host, AppShell, platform, render, input, audio, network, storage, diagnostics, and UI adapters. Present canonical target root; in... |
| `safety` | `transitional_contract_or_schema_root` | `contracts` | `split` | `CONVERGE-06` | `high` | Safety policy belongs under contracts or docs depending on authority. |
| `scripts` | `canonical` | `scripts` | `keep` | `none` | `low` | Developer workflow scripts and repository automation entrypoints. |
| `security` | `transitional_contract_or_schema_root` | `contracts` | `split` | `CONVERGE-06` | `high` | Security and trust surfaces are protected and review-sensitive. |
| `SECURITY.md` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |
| `server` | `transitional_product_root` | `apps` | `move` | `CONVERGE-08` | `medium` | Server authority semantics must stay governed by game/engine/runtime contracts. |
| `setup` | `transitional_product_root` | `apps` | `move` | `CONVERGE-08` | `medium` | Setup install identity and virtual roots must not change during moves. |
| `signals` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/signals; contracts/registries/signals; game/domains/signals; content/domain-data/signals; docs/domains/signals; tests/d... |
| `sitecustomize.py` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |
| `specs` | `transitional_contract_or_schema_root` | `contracts` | `split` | `CONVERGE-06` | `high` | Normative specs must retain authority; reality specs remain canonical over data projections. |
| `system` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/system; contracts/registries/system; game/domains/system; content/domain-data/system; docs/domains/system; tests/determ... |
| `templates` | `transitional_content_or_data_root` | `content` | `split` | `CONVERGE-09` | `high` | Templates may be authored content, contracts, or generated inputs. |
| `tests` | `canonical` | `tests` | `keep` | `none` | `low` | Test suites, determinism checks, fixtures, and verification evidence inputs. |
| `thermal` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/thermal; contracts/registries/thermal; game/domains/thermal; content/domain-data/thermal; docs/domains/thermal; tests/d... |
| `tool_ui_bind.cmd` | `unknown_needs_review` | `unknown` | `review` | `review` | `review` | No matching root classification in layout contract. |
| `tool_ui_doc_annotate.cmd` | `unknown_needs_review` | `unknown` | `review` | `review` | `review` | No matching root classification in layout contract. |
| `tool_ui_validate.cmd` | `unknown_needs_review` | `unknown` | `review` | `review` | `review` | No matching root classification in layout contract. |
| `tools` | `canonical` | `tools` | `keep` | `none` | `low` | Developer, validation, migration, CI, code generation, review, and audit tools. |
| `universe` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/universe; contracts/registries/universe; game/domains/universe; content/domain-data/universe; docs/domains/universe; te... |
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
| `worldgen` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/worldgen; contracts/registries/worldgen; game/domains/worldgen; content/domain-data/worldgen; docs/domains/worldgen; te... |

## Unknown Or Review Roots

- `__init__.py`: `unknown_needs_review` / `review`. No matching root classification in layout contract.
- `artifacts`: `generated_or_ephemeral` / `review`. Review before using as authority.
- `compat`: `transitional_contract_or_schema_root` / `review`. Root-level compat/ remains mixed implementation and shim code after CONVERGE-06; do not move wholesale into contracts/.
- `dist`: `generated_or_ephemeral` / `review`. Distribution output is governed by distribution contracts, not source repo layout.
- `governance`: `unknown_needs_review` / `review`. Governance mirrors must not compete with AGENTS.md or canon.
- `ide`: `unknown_needs_review` / `review`. IDE projections may belong under cmake, tools, or generated evidence depending on role.
- `labs`: `unknown_needs_review` / `review`. Experimental material requires review before binding.
- `lib`: `transitional_contract_or_schema_root` / `review`. Do not classify by name alone; inspect ownership first.
- `libs`: `transitional_contract_or_schema_root` / `review`. Do not classify by name alone; inspect ownership first.
- `locks`: `transitional_contract_or_schema_root` / `review`. Root-level locks/ remains review because it contains concrete deterministic pack lock artifacts, not only lockfile schemas.
- `meta`: `unknown_needs_review` / `review`. Meta surfaces require ownership review.
- `meta_extensions_engine.py`: `unknown_needs_review` / `review`. No matching root classification in layout contract.
- `numeric_discipline.py`: `unknown_needs_review` / `review`. No matching root classification in layout contract.
- `performance`: `unknown_needs_review` / `review`. Performance tooling and evidence should stay tool/evidence scoped.
- `tool_ui_bind.cmd`: `unknown_needs_review` / `review`. No matching root classification in layout contract.
- `tool_ui_doc_annotate.cmd`: `unknown_needs_review` / `review`. No matching root classification in layout contract.
- `tool_ui_validate.cmd`: `unknown_needs_review` / `review`. No matching root classification in layout contract.
- `validation`: `unknown_needs_review` / `review`. Validation tooling belongs under tools unless it is contract law.

## Split-Required Roots

- `astro` -> `contracts/game/content/docs/tests split` (`CONVERGE-09`): contracts/schemas/astro; contracts/registries/astro; game/domains/astro; content/domain-data/astro; docs/domains/astro; tests/determinism...
- `bundles` -> `content_or_exports_review` (`CONVERGE-09`): Authored bundles and generated exports require separate handling.
- `chem` -> `contracts/game/content/docs/tests split` (`CONVERGE-09`): contracts/schemas/chem; contracts/registries/chem; game/domains/chem; content/domain-data/chem; docs/domains/chem; tests/determinism/chem...
- `compat` -> `contracts/compatibility_plus_runtime_review` (`CONVERGE-06`): Root-level compat/ remains mixed implementation and shim code after CONVERGE-06; do not move wholesale into contracts/.
- `control` -> `runtime/control` (`CONVERGE-07`): Control substrate must preserve process-only mutation boundaries.
- `core` -> `runtime/core_or_game_domain_review` (`CONVERGE-07`): Core is likely mixed; do not move wholesale.
- `data` -> `content_or_runtime_store_review` (`CONVERGE-09`): Data contains registries, content, planning mirrors, and generated evidence; split by authority.
- `diegetics` -> `contracts/game/content/docs/tests split` (`CONVERGE-09`): contracts/schemas/diegetics; contracts/registries/diegetics; game/domains/diegetics; content/domain-data/diegetics; docs/domains/diegetic...
- `electric` -> `contracts/game/content/docs/tests split` (`CONVERGE-09`): contracts/schemas/electric; contracts/registries/electric; game/domains/electric; content/domain-data/electric; docs/domains/electric; te...
- `embodiment` -> `contracts/game/content/docs/tests split` (`CONVERGE-09`): contracts/schemas/embodiment; contracts/registries/embodiment; game/domains/embodiment; content/domain-data/embodiment; docs/domains/embo...
- `epistemics` -> `contracts/game/content/docs/tests split` (`CONVERGE-09`): contracts/schemas/epistemics; contracts/registries/epistemics; game/domains/epistemics; content/domain-data/epistemics; docs/domains/epis...
- `field` -> `contracts/game/content/docs/tests split` (`CONVERGE-09`): contracts/schemas/field; contracts/registries/field; game/domains/field; content/domain-data/field; docs/domains/field; tests/determinism...
- `fields` -> `contracts/game/content/docs/tests split` (`CONVERGE-09`): contracts/schemas/fields; contracts/registries/fields; game/domains/fields; content/domain-data/fields; docs/domains/fields; tests/determ...
- `fluid` -> `contracts/game/content/docs/tests split` (`CONVERGE-09`): contracts/schemas/fluid; contracts/registries/fluid; game/domains/fluid; content/domain-data/fluid; docs/domains/fluid; tests/determinism...
- `geo` -> `contracts/game/content/docs/tests split` (`CONVERGE-09`): contracts/schemas/geo; contracts/registries/geo; game/domains/geo; content/domain-data/geo; docs/domains/geo; tests/determinism/geo; test...
- `infrastructure` -> `contracts/game/content/docs/tests split` (`CONVERGE-09`): contracts/schemas/infrastructure; contracts/registries/infrastructure; game/domains/infrastructure; content/domain-data/infrastructure; d...
- `inspection` -> `contracts/game/content/docs/tests split` (`CONVERGE-09`): contracts/schemas/inspection; contracts/registries/inspection; game/domains/inspection; content/domain-data/inspection; docs/domains/insp...
- `interaction` -> `contracts/game/content/docs/tests split` (`CONVERGE-09`): contracts/schemas/interaction; contracts/registries/interaction; game/domains/interaction; content/domain-data/interaction; docs/domains/...
- `interior` -> `contracts/game/content/docs/tests split` (`CONVERGE-09`): contracts/schemas/interior; contracts/registries/interior; game/domains/interior; content/domain-data/interior; docs/domains/interior; te...
- `locks` -> `contracts/locks_or_store_locks_review` (`CONVERGE-06`): Root-level locks/ remains review because it contains concrete deterministic pack lock artifacts, not only lockfile schemas.
- `logic` -> `contracts/game/content/docs/tests split` (`CONVERGE-09`): contracts/schemas/logic; contracts/registries/logic; game/domains/logic; content/domain-data/logic; docs/domains/logic; tests/determinism...
- `logistics` -> `contracts/game/content/docs/tests split` (`CONVERGE-09`): contracts/schemas/logistics; contracts/registries/logistics; game/domains/logistics; content/domain-data/logistics; docs/domains/logistic...
- `machines` -> `contracts/game/content/docs/tests split` (`CONVERGE-09`): contracts/schemas/machines; contracts/registries/machines; game/domains/machines; content/domain-data/machines; docs/domains/machines; te...
- `materials` -> `contracts/game/content/docs/tests split` (`CONVERGE-09`): contracts/schemas/materials; contracts/registries/materials; game/domains/materials; content/domain-data/materials; docs/domains/material...
- `mechanics` -> `contracts/game/content/docs/tests split` (`CONVERGE-09`): contracts/schemas/mechanics; contracts/registries/mechanics; game/domains/mechanics; content/domain-data/mechanics; docs/domains/mechanic...
- `mobility` -> `contracts/game/content/docs/tests split` (`CONVERGE-09`): contracts/schemas/mobility; contracts/registries/mobility; game/domains/mobility; content/domain-data/mobility; docs/domains/mobility; te...
- `modding` -> `content/modding` (`CONVERGE-09`): Modding may include content, contracts, and docs.
- `net` -> `runtime/network` (`CONVERGE-07`): Root-level net/ remains mixed after CONVERGE-07 because it contains transport, anti-cheat, SRZ, and server-authoritative policy code; do...
- `packs` -> `content/packs` (`CONVERGE-09`): Current runtime pack substrate; pack ownership split remains review-sensitive.
- `physics` -> `contracts/game/content/docs/tests split` (`CONVERGE-09`): contracts/schemas/physics; contracts/registries/physics; game/domains/physics; content/domain-data/physics; docs/domains/physics; tests/d...
- `pollution` -> `contracts/game/content/docs/tests split` (`CONVERGE-09`): contracts/schemas/pollution; contracts/registries/pollution; game/domains/pollution; content/domain-data/pollution; docs/domains/pollutio...
- `process` -> `contracts/game/content/docs/tests split` (`CONVERGE-09`): contracts/schemas/process; contracts/registries/process; game/domains/process; content/domain-data/process; docs/domains/process; tests/d...
- `reality` -> `contracts/game/content/docs/tests split` (`CONVERGE-09`): contracts/schemas/reality; contracts/registries/reality; game/domains/reality; content/domain-data/reality; docs/domains/reality; tests/d...
- `repo` -> `split_to_contracts_docs_tools` (`CONVERGE-06`): Do not add new authority here; split later into contracts/repo, docs/repo, or tools/migration.
- `safety` -> `contracts/safety` (`CONVERGE-06`): Safety policy belongs under contracts or docs depending on authority.
- `security` -> `contracts/security` (`CONVERGE-06`): Security and trust surfaces are protected and review-sensitive.
- `signals` -> `contracts/game/content/docs/tests split` (`CONVERGE-09`): contracts/schemas/signals; contracts/registries/signals; game/domains/signals; content/domain-data/signals; docs/domains/signals; tests/d...
- `specs` -> `contracts/specs` (`CONVERGE-06`): Normative specs must retain authority; reality specs remain canonical over data projections.
- `system` -> `contracts/game/content/docs/tests split` (`CONVERGE-09`): contracts/schemas/system; contracts/registries/system; game/domains/system; content/domain-data/system; docs/domains/system; tests/determ...
- `templates` -> `content/templates` (`CONVERGE-09`): Templates may be authored content, contracts, or generated inputs.
- `thermal` -> `contracts/game/content/docs/tests split` (`CONVERGE-09`): contracts/schemas/thermal; contracts/registries/thermal; game/domains/thermal; content/domain-data/thermal; docs/domains/thermal; tests/d...
- `universe` -> `contracts/game/content/docs/tests split` (`CONVERGE-09`): contracts/schemas/universe; contracts/registries/universe; game/domains/universe; content/domain-data/universe; docs/domains/universe; te...
- `updates` -> `release_or_ops_review` (`review`): Update metadata belongs to release/control-plane ownership after review.
- `worldgen` -> `contracts/game/content/docs/tests split` (`CONVERGE-09`): contracts/schemas/worldgen; contracts/registries/worldgen; game/domains/worldgen; content/domain-data/worldgen; docs/domains/worldgen; te...

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

No moves are performed by this document.
