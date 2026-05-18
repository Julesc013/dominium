Status: DERIVED
Last Reviewed: 2026-05-16
Supersedes: none
Superseded By: none

# Move Map

Status: PROVISIONAL
Phase: CONVERGE-09
Machine-readable source: `tools/migration/root_move_map.json`

This document explains the generated move map. The map is a planning artifact: it records completed and future moves, but it does not execute moves by itself.

## CONVERGE-09 Note

CONVERGE-09 completed the safe portion of the domain-root split by moving pure Python domain implementation roots under `game/domains/`. Mixed review roots remain for later inspection; blocking validation remains CONVERGE-10.

Future migration sequence:

- CONVERGE-10 blocking validation after remaining review roots are resolved or explicitly excepted
- CONVERGE-11 product/platform/render/native/toolchain/package matrices
- CONVERGE-12 stale-doc and cross-reference cleanup

Distribution, install, media, portable-store, package-cache, bundle, and runtime projection layouts are handled by CONVERGE-04, not by this source-repo move map.

## Warnings

- Domain roots must not be moved wholesale unless proven pure; CONVERGE-09 moved only Python implementation roots after inspection.
- Product roots must remain thin after migration.
- Runtime roots must not own simulation truth.
- Distribution/install/media layouts are projections handled by CONVERGE-04.
- `dist/`, `build/`, `out/`, package caches, staging directories, media payloads, and runtime stores must not be confused with source ownership roots.

## Planning Table

| Current Path | Proposed Target | Action | Split? | Shim? | Status | Phase | Risk | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `.agentignore` | `.agentignore` | `retain_file` | `false` | `false` | `not_started` | `none` | `low` | Allowed root file. |
| `.aide` | `.aide` | `retain_metadata` | `false` | `false` | `not_started` | `none` | `low` | Allowed metadata/config root. |
| `.aide.local.example` | `.aide.local.example` | `retain_metadata` | `false` | `false` | `not_started` | `none` | `low` | Allowed metadata/config root. |
| `.gitattributes` | `.gitattributes` | `retain_file` | `false` | `false` | `not_started` | `none` | `low` | Allowed root file. |
| `.github` | `.github` | `retain_metadata` | `false` | `false` | `not_started` | `none` | `low` | Allowed metadata/config root. |
| `.gitignore` | `.gitignore` | `retain_file` | `false` | `false` | `not_started` | `none` | `low` | Allowed root file. |
| `.vscode` | `.vscode` | `retain_metadata` | `false` | `false` | `not_started` | `none` | `low` | Allowed metadata/config root. |
| `AGENTS.md` | `AGENTS.md` | `retain_file` | `false` | `false` | `not_started` | `none` | `low` | Allowed root file. |
| `app` | `runtime/app` | `move` | `false` | `false` | `completed` | `CONVERGE-07` | `medium` | Completed in CONVERGE-07; root-level app/ moved under runtime/app/. |
| `apps` | `apps` | `keep` | `false` | `false` | `not_started` | `none` | `low` | Thin product entrypoints and product composition surfaces. |
| `appshell` | `runtime/appshell` | `move` | `false` | `false` | `completed` | `CONVERGE-07` | `medium` | Completed in CONVERGE-07; root-level appshell/ moved under runtime/appshell/. |
| `archive` | `archive` | `keep` | `false` | `false` | `not_started` | `none` | `low` | Historical, superseded, quarantined, generated-evidence, and legacy material retained with provenance. |
| `artifacts` | `generated evidence or release artifact review` | `ignore_generated` | `false` | `false` | `not_started` | `review` | `review` | Review before using as authority. |
| `astro` | `game/domains/astronomy` | `split` | `true` | `false` | `completed` | `CONVERGE-09` | `medium` | Completed in CONVERGE-09; root-level astro/ implementation moved under game/domains/astronomy/. No schemas, registries, content data, or docs were found in that root during the... |
| `attic` | `archive/historical/attic` | `archive` | `false` | `false` | `completed` | `CONVERGE-05` | `low` | Completed in CONVERGE-05; root-level attic/ moved under archive/historical/attic/. |
| `audio` | `runtime/audio` | `review_absent` | `false` | `false` | `completed` | `CONVERGE-07` | `low` | Confirmed absent in CONVERGE-07; future source material belongs under runtime/audio/. |
| `bundles` | `content_or_exports_review` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | Authored bundles and generated exports require separate handling. |
| `CHANGELOG.md` | `CHANGELOG.md` | `retain_file` | `false` | `false` | `not_started` | `none` | `low` | Allowed root file. |
| `chem` | `game/domains/chemistry` | `split` | `true` | `false` | `completed` | `CONVERGE-09` | `medium` | Completed in CONVERGE-09; root-level chem/ implementation moved under game/domains/chemistry/. No schemas, registries, content data, or docs were found in that root during the s... |
| `CLAUDE.md` | `CLAUDE.md` | `retain_file` | `false` | `false` | `not_started` | `none` | `low` | Allowed root file. |
| `client` | `apps/client` | `move` | `false` | `false` | `completed` | `CONVERGE-08` | `medium` | Completed in CONVERGE-08; root-level client/ moved under apps/client/. |
| `cmake` | `cmake` | `keep` | `false` | `false` | `not_started` | `none` | `low` | CMake modules and build configuration helpers. |
| `CMakeLists.txt` | `CMakeLists.txt` | `retain_file` | `false` | `false` | `not_started` | `none` | `low` | Allowed root file. |
| `CMakePresets.json` | `CMakePresets.json` | `retain_file` | `false` | `false` | `not_started` | `none` | `low` | Allowed root file. |
| `CODE_CHANGE_JUSTIFICATION.md` | `CODE_CHANGE_JUSTIFICATION.md` | `retain_file` | `false` | `false` | `not_started` | `none` | `low` | Allowed root file. |
| `compat` | `contracts/compatibility_plus_runtime_review` | `review` | `true` | `true` | `review` | `CONVERGE-06` | `review` | Root-level compat/ remains mixed implementation and shim code after CONVERGE-06; do not move wholesale into contracts/. |
| `content` | `content` | `keep` | `false` | `false` | `not_started` | `none` | `low` | Authored packs, profiles, fixtures, datasets, assets, and domain data. |
| `contracts` | `contracts` | `keep` | `false` | `false` | `not_started` | `none` | `low` | Machine-readable and prose contracts for schemas, registries, protocols, compatibility, stability, replay, ABI, repository, and distribution rules. |
| `CONTRIBUTING.md` | `CONTRIBUTING.md` | `retain_file` | `false` | `false` | `not_started` | `none` | `low` | Allowed root file. |
| `control` | `runtime/control` | `split` | `true` | `true` | `not_started` | `CONVERGE-07` | `high` | Control substrate must preserve process-only mutation boundaries. |
| `core` | `runtime/core_or_game_domain_review` | `split` | `true` | `true` | `not_started` | `CONVERGE-07` | `high` | Core is likely mixed; do not move wholesale. |
| `data` | `content_or_runtime_store_review` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | Data contains registries, content, planning mirrors, and generated evidence; split by authority. |
| `diag` | `runtime/diagnostics` | `move` | `false` | `false` | `completed` | `CONVERGE-07` | `medium` | Completed in CONVERGE-07; root-level diag/ moved under runtime/diagnostics/. |
| `diagnostics` | `runtime/diagnostics` | `review_absent` | `false` | `false` | `completed` | `CONVERGE-07` | `low` | Confirmed absent in CONVERGE-07; future source material belongs under runtime/diagnostics/. |
| `diegetics` | `game/domains/diegetics` | `split` | `true` | `false` | `completed` | `CONVERGE-09` | `medium` | Completed in CONVERGE-09; root-level diegetics/ implementation moved under game/domains/diegetics/. No schemas, registries, content data, or docs were found in that root during... |
| `dist` | `generated distribution output; future distribution contract review` | `ignore_generated` | `false` | `false` | `not_started` | `review` | `review` | Distribution output is governed by distribution contracts, not source repo layout. |
| `docs` | `docs` | `keep` | `false` | `false` | `not_started` | `none` | `low` | Human-readable doctrine, guides, audits, and explanatory material. |
| `DOMINIUM.md` | `DOMINIUM.md` | `retain_file` | `false` | `false` | `not_started` | `none` | `low` | Allowed root file. |
| `electric` | `game/domains/electricity` | `split` | `true` | `false` | `completed` | `CONVERGE-09` | `medium` | Completed in CONVERGE-09; root-level electric/ implementation moved under game/domains/electricity/. No schemas, registries, content data, or docs were found in that root during... |
| `embodiment` | `game/domains/embodiment` | `split` | `true` | `false` | `completed` | `CONVERGE-09` | `medium` | Completed in CONVERGE-09; root-level embodiment/ implementation moved under game/domains/embodiment/. No schemas, registries, content data, or docs were found in that root durin... |
| `engine` | `engine` | `keep` | `false` | `false` | `not_started` | `none` | `low` | Deterministic Domino substrate and public engine contracts. |
| `epistemics` | `game/domains/epistemics` | `split` | `true` | `false` | `completed` | `CONVERGE-09` | `medium` | Completed in CONVERGE-09; root-level epistemics/ implementation moved under game/domains/epistemics/. No schemas, registries, content data, or docs were found in that root durin... |
| `field` | `game/domains/fields/from_root_field` | `split` | `true` | `false` | `completed` | `CONVERGE-09` | `medium` | Completed in CONVERGE-09; root-level field/ implementation moved under game/domains/fields/from_root_field/. No schemas, registries, content data, or docs were found in that roo... |
| `fields` | `game/domains/fields` | `split` | `true` | `false` | `completed` | `CONVERGE-09` | `medium` | Completed in CONVERGE-09; root-level fields/ implementation moved under game/domains/fields/. No schemas, registries, content data, or docs were found in that root during the sa... |
| `fluid` | `game/domains/fluids` | `split` | `true` | `false` | `completed` | `CONVERGE-09` | `medium` | Completed in CONVERGE-09; root-level fluid/ implementation moved under game/domains/fluids/. No schemas, registries, content data, or docs were found in that root during the saf... |
| `game` | `game` | `keep` | `false` | `false` | `not_started` | `none` | `low` | Dominium rules, domain process semantics, and authoritative game meaning. |
| `geo` | `game/domains/geology` | `split` | `true` | `false` | `completed` | `CONVERGE-09` | `medium` | Completed in CONVERGE-09; root-level geo/ implementation moved under game/domains/geology/. No schemas, registries, content data, or docs were found in that root during the safe... |
| `governance` | `docs/governance` | `review` | `false` | `false` | `review` | `review` | `review` | Governance mirrors must not compete with AGENTS.md or canon. |
| `GOVERNANCE.md` | `GOVERNANCE.md` | `retain_file` | `false` | `false` | `not_started` | `none` | `low` | Allowed root file. |
| `ide` | `cmake_or_tools_review` | `review` | `false` | `false` | `review` | `review` | `review` | IDE projections may belong under cmake, tools, or generated evidence depending on role. |
| `infrastructure` | `game/domains/infrastructure` | `split` | `true` | `false` | `completed` | `CONVERGE-09` | `medium` | Completed in CONVERGE-09; root-level infrastructure/ implementation moved under game/domains/infrastructure/. No schemas, registries, content data, or docs were found in that ro... |
| `input` | `runtime/input` | `review_absent` | `false` | `false` | `completed` | `CONVERGE-07` | `low` | Confirmed absent in CONVERGE-07; future source material belongs under runtime/input/. |
| `inspection` | `game/domains/inspection` | `split` | `true` | `false` | `completed` | `CONVERGE-09` | `medium` | Completed in CONVERGE-09; root-level inspection/ implementation moved under game/domains/inspection/. No schemas, registries, content data, or docs were found in that root durin... |
| `interaction` | `game/domains/interaction` | `split` | `true` | `false` | `completed` | `CONVERGE-09` | `medium` | Completed in CONVERGE-09; root-level interaction/ implementation moved under game/domains/interaction/. No schemas, registries, content data, or docs were found in that root dur... |
| `interior` | `game/domains/interior` | `split` | `true` | `false` | `completed` | `CONVERGE-09` | `medium` | Completed in CONVERGE-09; root-level interior/ implementation moved under game/domains/interior/. No schemas, registries, content data, or docs were found in that root during th... |
| `launcher` | `apps/launcher` | `move` | `false` | `false` | `completed` | `CONVERGE-08` | `medium` | Completed in CONVERGE-08; root-level launcher/ moved under apps/launcher/. |
| `legacy` | `archive/legacy` | `archive` | `false` | `false` | `completed` | `CONVERGE-05` | `low` | Completed in CONVERGE-05; root-level legacy/ moved under archive/legacy/. |
| `lib` | `review` | `review` | `false` | `true` | `review` | `CONVERGE-06` | `review` | Do not classify by name alone; inspect ownership first. |
| `libs` | `review` | `review` | `false` | `true` | `review` | `CONVERGE-06` | `review` | Do not classify by name alone; inspect ownership first. |
| `LICENSE.md` | `LICENSE.md` | `retain_file` | `false` | `false` | `not_started` | `none` | `low` | Allowed root file. |
| `locks` | `contracts/locks_or_store_locks_review` | `review` | `true` | `true` | `review` | `CONVERGE-06` | `review` | Root-level locks/ remains review because it contains concrete deterministic pack lock artifacts, not only lockfile schemas. |
| `logic` | `game/domains/logic` | `split` | `true` | `false` | `completed` | `CONVERGE-09` | `medium` | Completed in CONVERGE-09; root-level logic/ implementation moved under game/domains/logic/. No schemas, registries, content data, or docs were found in that root during the safe... |
| `logistics` | `game/domains/logistics` | `split` | `true` | `false` | `completed` | `CONVERGE-09` | `medium` | Completed in CONVERGE-09; root-level logistics/ implementation moved under game/domains/logistics/. No schemas, registries, content data, or docs were found in that root during... |
| `machines` | `game/domains/machines` | `split` | `true` | `false` | `completed` | `CONVERGE-09` | `medium` | Completed in CONVERGE-09; root-level machines/ implementation moved under game/domains/machines/. No schemas, registries, content data, or docs were found in that root during th... |
| `materials` | `game/domains/materials` | `split` | `true` | `false` | `completed` | `CONVERGE-09` | `medium` | Completed in CONVERGE-09; root-level materials/ implementation moved under game/domains/materials/. No schemas, registries, content data, or docs were found in that root during... |
| `mechanics` | `game/domains/mechanics` | `split` | `true` | `false` | `completed` | `CONVERGE-09` | `medium` | Completed in CONVERGE-09; root-level mechanics/ implementation moved under game/domains/mechanics/. No schemas, registries, content data, or docs were found in that root during... |
| `meta` | `review` | `review` | `false` | `false` | `review` | `review` | `review` | Meta surfaces require ownership review. |
| `meta_extensions_engine.py` | `review` | `review` | `false` | `false` | `review` | `review` | `review` | No matching root classification in layout contract. |
| `mobility` | `game/domains/mobility` | `split` | `true` | `false` | `completed` | `CONVERGE-09` | `medium` | Completed in CONVERGE-09; root-level mobility/ implementation moved under game/domains/mobility/. No schemas, registries, content data, or docs were found in that root during th... |
| `modding` | `content/modding` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | Modding may include content, contracts, and docs. |
| `MODDING.md` | `MODDING.md` | `retain_file` | `false` | `false` | `not_started` | `none` | `low` | Allowed root file. |
| `models` | `content/models` | `move` | `false` | `false` | `not_started` | `CONVERGE-09` | `medium` | Model data should be distinguished from generated or runtime state. |
| `net` | `runtime/network` | `split` | `true` | `true` | `not_started` | `CONVERGE-07` | `high` | Root-level net/ remains mixed after CONVERGE-07 because it contains transport, anti-cheat, SRZ, and server-authoritative policy code; do not move wholesale. |
| `network` | `runtime/network` | `review_absent` | `false` | `false` | `completed` | `CONVERGE-07` | `low` | Confirmed absent in CONVERGE-07; future source material belongs under runtime/network/. |
| `numeric_discipline.py` | `review` | `review` | `false` | `false` | `review` | `review` | `review` | No matching root classification in layout contract. |
| `packs` | `content/packs` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | Current runtime pack substrate; pack ownership split remains review-sensitive. |
| `performance` | `tools/performance` | `review` | `false` | `false` | `review` | `review` | `review` | Performance tooling and evidence should stay tool/evidence scoped. |
| `physics` | `game/domains/physics` | `split` | `true` | `false` | `completed` | `CONVERGE-09` | `medium` | Completed in CONVERGE-09; root-level physics/ implementation moved under game/domains/physics/. No schemas, registries, content data, or docs were found in that root during the... |
| `platform` | `runtime/platform` | `review_absent` | `false` | `false` | `completed` | `CONVERGE-07` | `low` | Confirmed absent in CONVERGE-07; future source material belongs under runtime/platform/. |
| `pollution` | `game/domains/pollution` | `split` | `true` | `false` | `completed` | `CONVERGE-09` | `medium` | Completed in CONVERGE-09; root-level pollution/ implementation moved under game/domains/pollution/. No schemas, registries, content data, or docs were found in that root during... |
| `process` | `game/domains/processes` | `split` | `true` | `false` | `completed` | `CONVERGE-09` | `medium` | Completed in CONVERGE-09; root-level process/ implementation moved under game/domains/processes/. No schemas, registries, content data, or docs were found in that root during th... |
| `profiles` | `content/profiles` | `move` | `false` | `false` | `not_started` | `CONVERGE-09` | `medium` | Profile data belongs under content unless runtime-store evidence proves otherwise. |
| `quarantine` | `archive/quarantine` | `archive` | `false` | `false` | `completed` | `CONVERGE-05` | `low` | Completed in CONVERGE-05; root-level quarantine/ moved under archive/quarantine/. |
| `README.md` | `README.md` | `retain_file` | `false` | `false` | `not_started` | `none` | `low` | Allowed root file. |
| `reality` | `game/domains/reality` | `split` | `true` | `false` | `completed` | `CONVERGE-09` | `medium` | Completed in CONVERGE-09; root-level reality/ implementation moved under game/domains/reality/. No schemas, registries, content data, or docs were found in that root during the... |
| `registries` | `contracts/registries` | `review_absent` | `false` | `false` | `completed` | `CONVERGE-06` | `low` | Confirmed absent in CONVERGE-06; future registry contracts belong under contracts/registries/. |
| `registry` | `contracts/registries` | `review_absent` | `false` | `false` | `completed` | `CONVERGE-06` | `low` | Confirmed absent in CONVERGE-06; future registry contracts belong under contracts/registries/. |
| `release` | `release` | `keep` | `false` | `false` | `not_started` | `none` | `low` | Release definitions, package recipes, matrices, signing metadata, and release policy inputs. |
| `render` | `runtime/render` | `review_absent` | `false` | `false` | `completed` | `CONVERGE-07` | `low` | Confirmed absent in CONVERGE-07; future source material belongs under runtime/render/. |
| `repo` | `split_to_contracts_docs_tools` | `split` | `true` | `true` | `not_started` | `CONVERGE-06` | `high` | Do not add new authority here; split later into contracts/repo, docs/repo, or tools/migration. |
| `runtime` | `runtime` | `keep` | `false` | `false` | `not_started` | `none` | `medium` | Runtime host, AppShell, platform, render, input, audio, network, storage, diagnostics, and UI adapters. Present canonical target root; inspect contents before treating adjacent... |
| `safety` | `contracts/safety` | `split` | `true` | `false` | `not_started` | `CONVERGE-06` | `high` | Safety policy belongs under contracts or docs depending on authority. |
| `schema` | `contracts/schemas` | `merge` | `false` | `false` | `completed` | `CONVERGE-06` | `medium` | Completed in CONVERGE-06; root-level schema/ moved under contracts/schemas/. |
| `schemas` | `contracts/schemas` | `merge` | `false` | `false` | `completed` | `CONVERGE-06` | `medium` | Completed in CONVERGE-06; root-level schemas/ merged under contracts/schemas/. |
| `scripts` | `scripts` | `keep` | `false` | `false` | `not_started` | `none` | `low` | Developer workflow scripts and repository automation entrypoints. |
| `security` | `contracts/security` | `split` | `true` | `false` | `not_started` | `CONVERGE-06` | `high` | Security and trust surfaces are protected and review-sensitive. |
| `SECURITY.md` | `SECURITY.md` | `retain_file` | `false` | `false` | `not_started` | `none` | `low` | Allowed root file. |
| `server` | `apps/server` | `move` | `false` | `false` | `completed` | `CONVERGE-08` | `medium` | Completed in CONVERGE-08; root-level server/ moved under apps/server/. |
| `setup` | `apps/setup` | `move` | `false` | `false` | `completed` | `CONVERGE-08` | `medium` | Completed in CONVERGE-08; root-level setup/ moved under apps/setup/. |
| `signals` | `game/domains/signals` | `split` | `true` | `false` | `completed` | `CONVERGE-09` | `medium` | Completed in CONVERGE-09; root-level signals/ implementation moved under game/domains/signals/. No schemas, registries, content data, or docs were found in that root during the... |
| `sitecustomize.py` | `sitecustomize.py` | `retain_file` | `false` | `false` | `not_started` | `none` | `low` | Allowed root file. |
| `specs` | `contracts/specs` | `split` | `true` | `false` | `not_started` | `CONVERGE-06` | `high` | Normative specs must retain authority; reality specs remain canonical over data projections. |
| `storage` | `runtime/storage` | `review_absent` | `false` | `false` | `completed` | `CONVERGE-07` | `low` | Confirmed absent in CONVERGE-07; future source material belongs under runtime/storage/. |
| `system` | `game/domains/systems` | `split` | `true` | `false` | `completed` | `CONVERGE-09` | `medium` | Completed in CONVERGE-09; root-level system/ implementation moved under game/domains/systems/. No schemas, registries, content data, or docs were found in that root during the s... |
| `templates` | `content/templates` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | Templates may be authored content, contracts, or generated inputs. |
| `tests` | `tests` | `keep` | `false` | `false` | `not_started` | `none` | `low` | Test suites, determinism checks, fixtures, and verification evidence inputs. |
| `thermal` | `game/domains/thermal` | `split` | `true` | `false` | `completed` | `CONVERGE-09` | `medium` | Completed in CONVERGE-09; root-level thermal/ implementation moved under game/domains/thermal/. No schemas, registries, content data, or docs were found in that root during the... |
| `tool_ui_bind.cmd` | `review` | `review` | `false` | `false` | `review` | `review` | `review` | No matching root classification in layout contract. |
| `tool_ui_doc_annotate.cmd` | `review` | `review` | `false` | `false` | `review` | `review` | `review` | No matching root classification in layout contract. |
| `tool_ui_validate.cmd` | `review` | `review` | `false` | `false` | `review` | `review` | `review` | No matching root classification in layout contract. |
| `tools` | `tools` | `keep` | `false` | `false` | `not_started` | `none` | `low` | Developer, validation, migration, CI, code generation, review, and audit tools. |
| `ui` | `runtime/ui` | `move` | `false` | `false` | `completed` | `CONVERGE-07` | `medium` | Completed in CONVERGE-07; root-level ui/ moved under runtime/ui/. |
| `universe` | `game/domains/universe` | `split` | `true` | `false` | `completed` | `CONVERGE-09` | `medium` | Completed in CONVERGE-09; root-level universe/ implementation moved under game/domains/universe/. No schemas, registries, content data, or docs were found in that root during th... |
| `updates` | `release_or_ops_review` | `split` | `true` | `false` | `not_started` | `review` | `high` | Update metadata belongs to release/control-plane ownership after review. |
| `validation` | `tools/validation` | `review` | `false` | `false` | `review` | `review` | `review` | Validation tooling belongs under tools unless it is contract law. |
| `VERSION_CLIENT` | `VERSION_CLIENT` | `retain_file` | `false` | `false` | `not_started` | `none` | `low` | Allowed root file. |
| `VERSION_ENGINE` | `VERSION_ENGINE` | `retain_file` | `false` | `false` | `not_started` | `none` | `low` | Allowed root file. |
| `VERSION_GAME` | `VERSION_GAME` | `retain_file` | `false` | `false` | `not_started` | `none` | `low` | Allowed root file. |
| `VERSION_LAUNCHER` | `VERSION_LAUNCHER` | `retain_file` | `false` | `false` | `not_started` | `none` | `low` | Allowed root file. |
| `VERSION_SERVER` | `VERSION_SERVER` | `retain_file` | `false` | `false` | `not_started` | `none` | `low` | Allowed root file. |
| `VERSION_SETUP` | `VERSION_SETUP` | `retain_file` | `false` | `false` | `not_started` | `none` | `low` | Allowed root file. |
| `VERSION_SUITE` | `VERSION_SUITE` | `retain_file` | `false` | `false` | `not_started` | `none` | `low` | Allowed root file. |
| `VERSION_TOOLS` | `VERSION_TOOLS` | `retain_file` | `false` | `false` | `not_started` | `none` | `low` | Allowed root file. |
| `worldgen` | `game/domains/worldgen` | `split` | `true` | `false` | `completed` | `CONVERGE-09` | `medium` | Completed in CONVERGE-09; root-level worldgen/ implementation moved under game/domains/worldgen/. No schemas, registries, content data, or docs were found in that root during th... |

## CONVERGE-10 Enforcement Note

CONVERGE-10 does not execute physical moves. It converts the remaining move-map review surface into explicit enforcement exceptions.

Remaining moves or splits are deferred behind `contracts/repo/layout_exceptions.toml`. Each active exception names the current path, target or review target, risk, and retirement phase. The main follow-up phase for exception retirement is CONVERGE-12 unless a narrower task retires an exception earlier.

Strict validators now pass with zero unexcepted violations. They will fail if a new root appears without contract/allowlist support or an active exception.

Future move-map focus:

- CONVERGE-11: product/platform/render/native/toolchain/package matrices.
- CONVERGE-12: retire or narrow remaining exceptions and reconcile stale cross-references.
- Future scoped tasks: split protected roots such as `compat/`, `control/`, `core/`, `data/`, `locks/`, `net/`, `packs/`, `repo/`, `security/`, and `specs/`.

## CONVERGE-11 Matrix Note

CONVERGE-11 added product, platform, render, native shell, toolchain, package, audio, input, network, storage, and distribution projection matrices. No physical moves occurred.

The move map remains about source repository roots. Matrix rows describe future expansion lanes and support posture after layout convergence; they do not define install/media/runtime projection directories and do not authorize new source roots.

Future move-map focus:

- CONVERGE-12: reconcile stale cross-references against the matrix and layout contracts.
- Future scoped tasks: retire active layout exceptions as roots are split, removed, or made canonical by reviewed contract updates.

## CONVERGE-12 Final Move-Map Status

CONVERGE-05 through CONVERGE-09 physical convergence phases are recorded as completed, partial, review, or exception-backed in the move map. CONVERGE-12 performed no physical moves.

Remaining move-map work is now post-CONVERGE exception retirement:

- review and retire active exceptions in `contracts/repo/layout_exceptions.toml`
- split or reclassify protected roots such as `compat/`, `control/`, `core/`, `data/`, `locks/`, `net/`, `packs/`, `repo/`, `security/`, and `specs/`
- keep historical path mentions out of current authority claims

Final audit: `docs/repo/audits/CONVERGE_12_FINAL_AUDIT.md`.

## POST-CONVERGE-01 Generated Output Cleanup

POST-CONVERGE-01 removed ignored, untracked generated/cache roots `.xstack_cache/`, `build/`, and `out/`. These paths now remain only as retired audit entries in `contracts/repo/layout_exceptions.toml`.

The active generated/output move-map review surface is now:

- `artifacts/`: active review, tracked toolchain-run provenance.
- `dist/`: active review, tracked distribution projection files.

No source roots were moved, and no product, runtime, domain, contract, or support-matrix semantics changed.

## POST-CONVERGE-02 Wrapper / Tooling / Governance Cleanup

POST-CONVERGE-02 retired the root package marker and moved quarantined labs documentation to the archive:

- `__init__.py`: removed after reference review found no in-repo import dependency.
- `labs/README.md`: moved to `archive/historical/labs/README.md`.
- `tool_ui_bind.cmd`, `tool_ui_doc_annotate.cmd`, and `tool_ui_validate.cmd`: retained as documented root compatibility shims.
- `governance`, `ide`, `meta`, `meta_extensions_engine.py`, `numeric_discipline.py`, `performance`, and `validation`: retained as active review exceptions because references remain live or protected.

No product, runtime, domain, contract, build-preset, or support-matrix semantics changed.

## POST-CONVERGE-03 Content / Pack / Profile / Bundle Cleanup

POST-CONVERGE-03 performed no physical content/package/profile/bundle moves. The generic move-map targets for the target roots remain review targets only and must not be executed without a later protected ownership task.

- `data`: still requires file-family split review.
- `packs`: still preserves runtime-packaging scope; do not collapse with `data/packs` without human review.
- `profiles`: still preserves `content/profiles/bundles/bundle.mvp_default.json` identity, hashes, and rel-path metadata.
- `bundles`: still preserves bundle IDs and lock/dependency semantics.
- `modding` and `models`: active implementation packages, not content-only move candidates.
- `templates`: protected-reference-backed root template surface.

No pack IDs, profile IDs, bundle IDs, content hashes, build semantics, or support-matrix semantics changed.

## POST-CONVERGE-04 Compat / Lib / Specs / Security / Update Cleanup

POST-CONVERGE-04 performed no physical high-risk moves. The move-map targets for these roots remain protected review targets only and must not be executed without a later ownership task that can preserve compatibility, security, safety, update, lock, ABI, and build semantics.

- `compat`: active implementation and shims; pure contracts may move only after compatibility review.
- `lib`: active Python install/save/store/bundle/artifact implementation; do not move without runtime/tooling import review.
- `libs`: CMake and ABI-critical C/C++ libraries and public headers; do not move without build/interface review.
- `locks`: concrete pack lock artifact with embedded identity and distribution copy behavior.
- `repo`: release policy, RepoX rulesets/exemptions, and canon state control-plane material.
- `safety`, `security`, and `specs`: protected semantic roots requiring explicit review.
- `updates`: tracked RepoX-generated update feeds referenced by release/update tooling.

No compatibility, security, safety, update, lockfile, ABI, build, product, runtime, or support-matrix semantics changed.

## POST-CONVERGE-05 Core / Control / Net Ownership Review

POST-CONVERGE-05 performed no physical core/control/net moves. The move-map targets for these roots remain protected review targets only and must not be executed without a later ownership task that can preserve deterministic substrate, process-only mutation, authority, network protocol, server, anti-cheat, SRZ, resync, and replay semantics.

- `core`: active deterministic substrate used by game domains, tools, and XStack session runtime.
- `control`: active control gateway, Control IR, negotiation, fidelity, planning, capability, view, effects, and proof implementation.
- `net`: active transport, server-authoritative, lockstep, SRZ hybrid, anti-cheat, shard coordination, and deterministic network test-harness implementation.

No product, runtime, engine, domain, build, ABI, process, authority, network, server, integrity, SRZ, or support-matrix semantics changed.
