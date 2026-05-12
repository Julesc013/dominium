# Root Inventory

Status: PROVISIONAL
Phase: CONVERGE-03
Machine-readable source: `tools/migration/root_inventory.json`

This document explains the generated inventory. The machine-readable contract and JSON inventory remain the source for validators and later migration planning.

No directories were moved, renamed, deleted, or rehomed in CONVERGE-03.

## Summary Counts

| Classification | Count |
| --- | ---: |
| `allowed_file` | 25 |
| `canonical` | 11 |
| `generated_or_ephemeral` | 2 |
| `metadata` | 4 |
| `split_required_domain_root` | 29 |
| `transitional_archive_or_quarantine_root` | 3 |
| `transitional_content_or_data_root` | 7 |
| `transitional_contract_or_schema_root` | 10 |
| `transitional_product_root` | 4 |
| `transitional_release_or_dist_root` | 1 |
| `transitional_runtime_root` | 7 |
| `unknown_needs_review` | 12 |

Total classified top-level entries: 115.

## All Root Entries

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
| `app` | `transitional_runtime_root` | `runtime` | `move` | `CONVERGE-07` | `medium` | Current runtime/app substrate; do not move in CONVERGE-01. |
| `appshell` | `transitional_runtime_root` | `runtime` | `move` | `CONVERGE-07` | `medium` | AppShell should converge under runtime after boundary proof. |
| `archive` | `canonical` | `archive` | `keep` | `none` | `low` | Historical, superseded, quarantined, generated-evidence, and legacy material retained with pr... |
| `artifacts` | `generated_or_ephemeral` | `generated` | `ignore_generated` | `review` | `review` | Review before using as authority. |
| `astro` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/astro; contracts/registries/astro; game/domains/astro; content/domain-data/... |
| `attic` | `transitional_archive_or_quarantine_root` | `archive` | `archive` | `CONVERGE-05` | `low` | Historical material should converge under archive. |
| `bundles` | `transitional_content_or_data_root` | `content` | `split` | `CONVERGE-09` | `high` | Authored bundles and generated exports require separate handling. |
| `CHANGELOG.md` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |
| `chem` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/chem; contracts/registries/chem; game/domains/chem; content/domain-data/che... |
| `CLAUDE.md` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |
| `client` | `transitional_product_root` | `apps` | `move` | `CONVERGE-08` | `medium` | Only thin product binding should remain under apps. |
| `cmake` | `canonical` | `cmake` | `keep` | `none` | `low` | CMake modules and build configuration helpers. |
| `CMakeLists.txt` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |
| `CMakePresets.json` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |
| `CODE_CHANGE_JUSTIFICATION.md` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |
| `compat` | `transitional_contract_or_schema_root` | `contracts` | `split` | `CONVERGE-06` | `high` | Compatibility meaning belongs in contracts; runtime adapters may move separately. |
| `contracts` | `canonical` | `contracts` | `keep` | `none` | `low` | Machine-readable and prose contracts for schemas, registries, protocols, compatibility, stabi... |
| `CONTRIBUTING.md` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |
| `control` | `transitional_runtime_root` | `runtime` | `split` | `CONVERGE-07` | `high` | Control substrate must preserve process-only mutation boundaries. |
| `core` | `transitional_runtime_root` | `runtime` | `split` | `CONVERGE-07` | `high` | Core is likely mixed; do not move wholesale. |
| `data` | `transitional_content_or_data_root` | `content` | `split` | `CONVERGE-09` | `high` | Data contains registries, content, planning mirrors, and generated evidence; split by authority. |
| `diag` | `transitional_runtime_root` | `runtime` | `move` | `CONVERGE-07` | `medium` | Diagnostics belong under runtime if they do not own truth. |
| `diegetics` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/diegetics; contracts/registries/diegetics; game/domains/diegetics; content/... |
| `dist` | `generated_or_ephemeral` | `generated` | `ignore_generated` | `review` | `review` | Distribution output is governed by distribution contracts, not source repo layout. |
| `docs` | `canonical` | `docs` | `keep` | `none` | `low` | Human-readable doctrine, guides, audits, and explanatory material. |
| `DOMINIUM.md` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |
| `electric` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/electric; contracts/registries/electric; game/domains/electric; content/dom... |
| `embodiment` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/embodiment; contracts/registries/embodiment; game/domains/embodiment; conte... |
| `engine` | `canonical` | `engine` | `keep` | `none` | `low` | Deterministic Domino substrate and public engine contracts. |
| `epistemics` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/epistemics; contracts/registries/epistemics; game/domains/epistemics; conte... |
| `field` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/field; contracts/registries/field; game/domains/field; content/domain-data/... |
| `fields` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/fields; contracts/registries/fields; game/domains/fields; content/domain-da... |
| `fluid` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/fluid; contracts/registries/fluid; game/domains/fluid; content/domain-data/... |
| `game` | `canonical` | `game` | `keep` | `none` | `low` | Dominium rules, domain process semantics, and authoritative game meaning. |
| `geo` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/geo; contracts/registries/geo; game/domains/geo; content/domain-data/geo; d... |
| `governance` | `unknown_needs_review` | `unknown` | `review` | `review` | `review` | Governance mirrors must not compete with AGENTS.md or canon. |
| `GOVERNANCE.md` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |
| `ide` | `unknown_needs_review` | `unknown` | `review` | `review` | `review` | IDE projections may belong under cmake, tools, or generated evidence depending on role. |
| `infrastructure` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/infrastructure; contracts/registries/infrastructure; game/domains/infrastru... |
| `inspection` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/inspection; contracts/registries/inspection; game/domains/inspection; conte... |
| `interaction` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/interaction; contracts/registries/interaction; game/domains/interaction; co... |
| `interior` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/interior; contracts/registries/interior; game/domains/interior; content/dom... |
| `labs` | `unknown_needs_review` | `unknown` | `review` | `review` | `review` | Experimental material requires review before binding. |
| `launcher` | `transitional_product_root` | `apps` | `move` | `CONVERGE-08` | `medium` | Launcher product identity and executable naming must remain stable. |
| `legacy` | `transitional_archive_or_quarantine_root` | `archive` | `archive` | `CONVERGE-05` | `low` | Legacy material should converge under archive. |
| `lib` | `transitional_contract_or_schema_root` | `unknown` | `review` | `CONVERGE-06` | `review` | Do not classify by name alone; inspect ownership first. |
| `libs` | `transitional_contract_or_schema_root` | `unknown` | `review` | `CONVERGE-06` | `review` | Do not classify by name alone; inspect ownership first. |
| `LICENSE.md` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |
| `locks` | `transitional_contract_or_schema_root` | `contracts` | `split` | `CONVERGE-06` | `high` | Deterministic locks, runtime locks, and ops transactions require separate homes. |
| `logic` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/logic; contracts/registries/logic; game/domains/logic; content/domain-data/... |
| `logistics` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/logistics; contracts/registries/logistics; game/domains/logistics; content/... |
| `machines` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/machines; contracts/registries/machines; game/domains/machines; content/dom... |
| `materials` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/materials; contracts/registries/materials; game/domains/materials; content/... |
| `mechanics` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/mechanics; contracts/registries/mechanics; game/domains/mechanics; content/... |
| `meta` | `unknown_needs_review` | `unknown` | `review` | `review` | `review` | Meta surfaces require ownership review. |
| `meta_extensions_engine.py` | `unknown_needs_review` | `unknown` | `review` | `review` | `review` | No matching root classification in layout contract. |
| `mobility` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/mobility; contracts/registries/mobility; game/domains/mobility; content/dom... |
| `modding` | `transitional_content_or_data_root` | `content` | `split` | `CONVERGE-09` | `high` | Modding may include content, contracts, and docs. |
| `MODDING.md` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |
| `models` | `transitional_content_or_data_root` | `content` | `move` | `CONVERGE-09` | `medium` | Model data should be distinguished from generated or runtime state. |
| `net` | `transitional_runtime_root` | `runtime` | `move` | `CONVERGE-07` | `medium` | Network adapters belong under runtime after authority boundaries are checked. |
| `numeric_discipline.py` | `unknown_needs_review` | `unknown` | `review` | `review` | `review` | No matching root classification in layout contract. |
| `packs` | `transitional_content_or_data_root` | `content` | `split` | `CONVERGE-09` | `high` | Current runtime pack substrate; pack ownership split remains review-sensitive. |
| `performance` | `unknown_needs_review` | `unknown` | `review` | `review` | `review` | Performance tooling and evidence should stay tool/evidence scoped. |
| `physics` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/physics; contracts/registries/physics; game/domains/physics; content/domain... |
| `pollution` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/pollution; contracts/registries/pollution; game/domains/pollution; content/... |
| `process` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/process; contracts/registries/process; game/domains/process; content/domain... |
| `profiles` | `transitional_content_or_data_root` | `content` | `move` | `CONVERGE-09` | `medium` | Profile data belongs under content unless runtime-store evidence proves otherwise. |
| `quarantine` | `transitional_archive_or_quarantine_root` | `archive` | `archive` | `CONVERGE-05` | `low` | Quarantined material should remain visible and provenance-preserved. |
| `README.md` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |
| `reality` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/reality; contracts/registries/reality; game/domains/reality; content/domain... |
| `release` | `canonical` | `release` | `keep` | `none` | `low` | Release definitions, package recipes, matrices, signing metadata, and release policy inputs. |
| `repo` | `transitional_contract_or_schema_root` | `contracts` | `split` | `CONVERGE-06` | `high` | Do not add new authority here; split later into contracts/repo, docs/repo, or tools/migration. |
| `runtime` | `canonical` | `runtime` | `keep` | `none` | `medium` | Runtime host, AppShell, platform, render, input, audio, network, storage, diagnostics, and UI... |
| `safety` | `transitional_contract_or_schema_root` | `contracts` | `split` | `CONVERGE-06` | `high` | Safety policy belongs under contracts or docs depending on authority. |
| `schema` | `transitional_contract_or_schema_root` | `contracts` | `merge` | `CONVERGE-06` | `high` | Current canonical schema law root; future physical convergence must preserve semantic authority. |
| `schemas` | `transitional_contract_or_schema_root` | `contracts` | `merge` | `CONVERGE-06` | `high` | Current validator-facing schema projection; must not replace schema law silently. |
| `scripts` | `canonical` | `scripts` | `keep` | `none` | `low` | Developer workflow scripts and repository automation entrypoints. |
| `security` | `transitional_contract_or_schema_root` | `contracts` | `split` | `CONVERGE-06` | `high` | Security and trust surfaces are protected and review-sensitive. |
| `SECURITY.md` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |
| `server` | `transitional_product_root` | `apps` | `move` | `CONVERGE-08` | `medium` | Server authority semantics must stay governed by game/engine/runtime contracts. |
| `setup` | `transitional_product_root` | `apps` | `move` | `CONVERGE-08` | `medium` | Setup install identity and virtual roots must not change during moves. |
| `signals` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/signals; contracts/registries/signals; game/domains/signals; content/domain... |
| `sitecustomize.py` | `allowed_file` | `metadata` | `retain_file` | `none` | `low` | Allowed root file. |
| `specs` | `transitional_contract_or_schema_root` | `contracts` | `split` | `CONVERGE-06` | `high` | Normative specs must retain authority; reality specs remain canonical over data projections. |
| `system` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/system; contracts/registries/system; game/domains/system; content/domain-da... |
| `templates` | `transitional_content_or_data_root` | `content` | `split` | `CONVERGE-09` | `high` | Templates may be authored content, contracts, or generated inputs. |
| `tests` | `canonical` | `tests` | `keep` | `none` | `low` | Test suites, determinism checks, fixtures, and verification evidence inputs. |
| `thermal` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/thermal; contracts/registries/thermal; game/domains/thermal; content/domain... |
| `tool_ui_bind.cmd` | `unknown_needs_review` | `unknown` | `review` | `review` | `review` | No matching root classification in layout contract. |
| `tool_ui_doc_annotate.cmd` | `unknown_needs_review` | `unknown` | `review` | `review` | `review` | No matching root classification in layout contract. |
| `tool_ui_validate.cmd` | `unknown_needs_review` | `unknown` | `review` | `review` | `review` | No matching root classification in layout contract. |
| `tools` | `canonical` | `tools` | `keep` | `none` | `low` | Developer, validation, migration, CI, code generation, review, and audit tools. |
| `ui` | `transitional_runtime_root` | `runtime` | `move` | `CONVERGE-07` | `medium` | UI is presentation/adaptation only and must not mutate truth. |
| `universe` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/universe; contracts/registries/universe; game/domains/universe; content/dom... |
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
| `worldgen` | `split_required_domain_root` | `mixed_split_required` | `split` | `CONVERGE-09` | `high` | contracts/schemas/worldgen; contracts/registries/worldgen; game/domains/worldgen; content/dom... |

## Unknown Or Review Roots

These entries need manual ownership review before later convergence phases bind them to a final home.

| Root | Classification | Proposed target | Reason |
| --- | --- | --- | --- |
| `__init__.py` | `unknown_needs_review` | `review` | No matching root classification in layout contract. |
| `artifacts` | `generated_or_ephemeral` | `generated evidence or release artifact review` | Review before using as authority. |
| `dist` | `generated_or_ephemeral` | `generated distribution output; future distribution contract review` | Distribution output is governed by distribution contracts, not source repo layout. |
| `governance` | `unknown_needs_review` | `docs/governance` | Governance mirrors must not compete with AGENTS.md or canon. |
| `ide` | `unknown_needs_review` | `cmake_or_tools_review` | IDE projections may belong under cmake, tools, or generated evidence depending on role. |
| `labs` | `unknown_needs_review` | `review` | Experimental material requires review before binding. |
| `lib` | `transitional_contract_or_schema_root` | `review` | Do not classify by name alone; inspect ownership first. |
| `libs` | `transitional_contract_or_schema_root` | `review` | Do not classify by name alone; inspect ownership first. |
| `meta` | `unknown_needs_review` | `review` | Meta surfaces require ownership review. |
| `meta_extensions_engine.py` | `unknown_needs_review` | `review` | No matching root classification in layout contract. |
| `numeric_discipline.py` | `unknown_needs_review` | `review` | No matching root classification in layout contract. |
| `performance` | `unknown_needs_review` | `tools/performance` | Performance tooling and evidence should stay tool/evidence scoped. |
| `tool_ui_bind.cmd` | `unknown_needs_review` | `review` | No matching root classification in layout contract. |
| `tool_ui_doc_annotate.cmd` | `unknown_needs_review` | `review` | No matching root classification in layout contract. |
| `tool_ui_validate.cmd` | `unknown_needs_review` | `review` | No matching root classification in layout contract. |
| `validation` | `unknown_needs_review` | `tools/validation` | Validation tooling belongs under tools unless it is contract law. |

## Split-Required Domain Roots

These roots are treated as mixed domain roots. They must be split across contracts, game implementation, content, docs, tests, and fixtures instead of moved wholesale.

| Root | Phase | Risk | Target model |
| --- | --- | --- | --- |
| `astro` | `CONVERGE-09` | `high` | `contracts/game/content/docs/tests split` |
| `chem` | `CONVERGE-09` | `high` | `contracts/game/content/docs/tests split` |
| `diegetics` | `CONVERGE-09` | `high` | `contracts/game/content/docs/tests split` |
| `electric` | `CONVERGE-09` | `high` | `contracts/game/content/docs/tests split` |
| `embodiment` | `CONVERGE-09` | `high` | `contracts/game/content/docs/tests split` |
| `epistemics` | `CONVERGE-09` | `high` | `contracts/game/content/docs/tests split` |
| `field` | `CONVERGE-09` | `high` | `contracts/game/content/docs/tests split` |
| `fields` | `CONVERGE-09` | `high` | `contracts/game/content/docs/tests split` |
| `fluid` | `CONVERGE-09` | `high` | `contracts/game/content/docs/tests split` |
| `geo` | `CONVERGE-09` | `high` | `contracts/game/content/docs/tests split` |
| `infrastructure` | `CONVERGE-09` | `high` | `contracts/game/content/docs/tests split` |
| `inspection` | `CONVERGE-09` | `high` | `contracts/game/content/docs/tests split` |
| `interaction` | `CONVERGE-09` | `high` | `contracts/game/content/docs/tests split` |
| `interior` | `CONVERGE-09` | `high` | `contracts/game/content/docs/tests split` |
| `logic` | `CONVERGE-09` | `high` | `contracts/game/content/docs/tests split` |
| `logistics` | `CONVERGE-09` | `high` | `contracts/game/content/docs/tests split` |
| `machines` | `CONVERGE-09` | `high` | `contracts/game/content/docs/tests split` |
| `materials` | `CONVERGE-09` | `high` | `contracts/game/content/docs/tests split` |
| `mechanics` | `CONVERGE-09` | `high` | `contracts/game/content/docs/tests split` |
| `mobility` | `CONVERGE-09` | `high` | `contracts/game/content/docs/tests split` |
| `physics` | `CONVERGE-09` | `high` | `contracts/game/content/docs/tests split` |
| `pollution` | `CONVERGE-09` | `high` | `contracts/game/content/docs/tests split` |
| `process` | `CONVERGE-09` | `high` | `contracts/game/content/docs/tests split` |
| `reality` | `CONVERGE-09` | `high` | `contracts/game/content/docs/tests split` |
| `signals` | `CONVERGE-09` | `high` | `contracts/game/content/docs/tests split` |
| `system` | `CONVERGE-09` | `high` | `contracts/game/content/docs/tests split` |
| `thermal` | `CONVERGE-09` | `high` | `contracts/game/content/docs/tests split` |
| `universe` | `CONVERGE-09` | `high` | `contracts/game/content/docs/tests split` |
| `worldgen` | `CONVERGE-09` | `high` | `contracts/game/content/docs/tests split` |

## Generated Or Ephemeral Roots

Generated roots are not source repository ownership authority. Later phases may ignore, clean, or preserve them only after provenance review.

| Root | Proposed target | Action | Notes |
| --- | --- | --- | --- |
| `artifacts` | `generated evidence or release artifact review` | `ignore_generated` | Review before using as authority. |
| `dist` | `generated distribution output; future distribution contract review` | `ignore_generated` | Distribution output is governed by distribution contracts, not source repo layout. |

## Metadata And Root Files

Metadata directories and allowed root files are retained at the repository root unless a later explicit policy changes them.

| Entry | Kind | Classification | Action |
| --- | --- | --- | --- |
| `.agentignore` | `file` | `allowed_file` | `retain_file` |
| `.aide` | `directory` | `metadata` | `retain_metadata` |
| `.aide.local.example` | `directory` | `metadata` | `retain_metadata` |
| `.gitattributes` | `file` | `allowed_file` | `retain_file` |
| `.github` | `directory` | `metadata` | `retain_metadata` |
| `.gitignore` | `file` | `allowed_file` | `retain_file` |
| `.vscode` | `directory` | `metadata` | `retain_metadata` |
| `AGENTS.md` | `file` | `allowed_file` | `retain_file` |
| `CHANGELOG.md` | `file` | `allowed_file` | `retain_file` |
| `CLAUDE.md` | `file` | `allowed_file` | `retain_file` |
| `CMakeLists.txt` | `file` | `allowed_file` | `retain_file` |
| `CMakePresets.json` | `file` | `allowed_file` | `retain_file` |
| `CODE_CHANGE_JUSTIFICATION.md` | `file` | `allowed_file` | `retain_file` |
| `CONTRIBUTING.md` | `file` | `allowed_file` | `retain_file` |
| `DOMINIUM.md` | `file` | `allowed_file` | `retain_file` |
| `GOVERNANCE.md` | `file` | `allowed_file` | `retain_file` |
| `LICENSE.md` | `file` | `allowed_file` | `retain_file` |
| `MODDING.md` | `file` | `allowed_file` | `retain_file` |
| `README.md` | `file` | `allowed_file` | `retain_file` |
| `SECURITY.md` | `file` | `allowed_file` | `retain_file` |
| `sitecustomize.py` | `file` | `allowed_file` | `retain_file` |
| `VERSION_CLIENT` | `file` | `allowed_file` | `retain_file` |
| `VERSION_ENGINE` | `file` | `allowed_file` | `retain_file` |
| `VERSION_GAME` | `file` | `allowed_file` | `retain_file` |
| `VERSION_LAUNCHER` | `file` | `allowed_file` | `retain_file` |
| `VERSION_SERVER` | `file` | `allowed_file` | `retain_file` |
| `VERSION_SETUP` | `file` | `allowed_file` | `retain_file` |
| `VERSION_SUITE` | `file` | `allowed_file` | `retain_file` |
| `VERSION_TOOLS` | `file` | `allowed_file` | `retain_file` |
