# Move Map

Status: PROVISIONAL
Phase: CONVERGE-08
Machine-readable source: `tools/migration/root_move_map.json`

This document explains the generated move map. The map is a planning artifact: it records completed and future moves, but it does not execute moves by itself.

## CONVERGE-08 Note

CONVERGE-08 completed product entrypoint convergence for root-level `client/`, `server/`, `setup/`, and `launcher/`. Product source now lives under `apps/`; domain roots remain for CONVERGE-09 and blocking validation remains for CONVERGE-10.

Future migration sequence:

- CONVERGE-09 domain split into contracts/game/content/docs/tests
- CONVERGE-10 blocking validation after controlled moves
- CONVERGE-11 product/platform/render/native/toolchain/package matrices
- CONVERGE-12 stale-doc and cross-reference cleanup

Distribution, install, media, portable-store, package-cache, bundle, and runtime projection layouts are handled by CONVERGE-04, not by this source-repo move map.

## Warnings

- Domain roots must not be moved wholesale unless proven pure.
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
| `__init__.py` | `review` | `review` | `false` | `false` | `review` | `review` | `review` | No matching root classification in layout contract. |
| `AGENTS.md` | `AGENTS.md` | `retain_file` | `false` | `false` | `not_started` | `none` | `low` | Allowed root file. |
| `app` | `runtime/app` | `move` | `false` | `false` | `completed` | `CONVERGE-07` | `medium` | Completed in CONVERGE-07; root-level app/ moved under runtime/app/. |
| `apps` | `apps` | `keep` | `false` | `false` | `not_started` | `none` | `low` | Thin product entrypoints and product composition surfaces. |
| `appshell` | `runtime/appshell` | `move` | `false` | `false` | `completed` | `CONVERGE-07` | `medium` | Completed in CONVERGE-07; root-level appshell/ moved under runtime/appshell/. |
| `archive` | `archive` | `keep` | `false` | `false` | `not_started` | `none` | `low` | Historical, superseded, quarantined, generated-evidence, and legacy material retained with provenance. |
| `artifacts` | `generated evidence or release artifact review` | `ignore_generated` | `false` | `false` | `not_started` | `review` | `review` | Review before using as authority. |
| `astro` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | contracts/schemas/astro; contracts/registries/astro; game/domains/astro; content/domain-data/astro; docs/domains/astro; tests/determinism/astro; tests/fixtur... |
| `attic` | `archive/historical/attic` | `archive` | `false` | `false` | `completed` | `CONVERGE-05` | `low` | Completed in CONVERGE-05; root-level attic/ moved under archive/historical/attic/. |
| `audio` | `runtime/audio` | `review_absent` | `false` | `false` | `completed` | `CONVERGE-07` | `low` | Confirmed absent in CONVERGE-07; future source material belongs under runtime/audio/. |
| `build` | `generated build output` | `ignore_generated` | `false` | `false` | `not_started` | `review` | `review` | Must not be treated as source repository ownership. |
| `bundles` | `content_or_exports_review` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | Authored bundles and generated exports require separate handling. |
| `CHANGELOG.md` | `CHANGELOG.md` | `retain_file` | `false` | `false` | `not_started` | `none` | `low` | Allowed root file. |
| `chem` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | contracts/schemas/chem; contracts/registries/chem; game/domains/chem; content/domain-data/chem; docs/domains/chem; tests/determinism/chem; tests/fixtures/chem |
| `CLAUDE.md` | `CLAUDE.md` | `retain_file` | `false` | `false` | `not_started` | `none` | `low` | Allowed root file. |
| `client` | `apps/client` | `move` | `false` | `false` | `completed` | `CONVERGE-08` | `medium` | Completed in CONVERGE-08; root-level client/ moved under apps/client/. |
| `cmake` | `cmake` | `keep` | `false` | `false` | `not_started` | `none` | `low` | CMake modules and build configuration helpers. |
| `CMakeLists.txt` | `CMakeLists.txt` | `retain_file` | `false` | `false` | `not_started` | `none` | `low` | Allowed root file. |
| `CMakePresets.json` | `CMakePresets.json` | `retain_file` | `false` | `false` | `not_started` | `none` | `low` | Allowed root file. |
| `CODE_CHANGE_JUSTIFICATION.md` | `CODE_CHANGE_JUSTIFICATION.md` | `retain_file` | `false` | `false` | `not_started` | `none` | `low` | Allowed root file. |
| `compat` | `contracts/compatibility_plus_runtime_review` | `review` | `true` | `true` | `review` | `CONVERGE-06` | `review` | Root-level compat/ remains mixed implementation and shim code after CONVERGE-06; do not move wholesale into contracts/. |
| `contracts` | `contracts` | `keep` | `false` | `false` | `not_started` | `none` | `low` | Machine-readable and prose contracts for schemas, registries, protocols, compatibility, stability, replay, ABI, repository, and distribution rules. |
| `CONTRIBUTING.md` | `CONTRIBUTING.md` | `retain_file` | `false` | `false` | `not_started` | `none` | `low` | Allowed root file. |
| `control` | `runtime/control` | `split` | `true` | `true` | `not_started` | `CONVERGE-07` | `high` | Control substrate must preserve process-only mutation boundaries. |
| `core` | `runtime/core_or_game_domain_review` | `split` | `true` | `true` | `not_started` | `CONVERGE-07` | `high` | Core is likely mixed; do not move wholesale. |
| `data` | `content_or_runtime_store_review` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | Data contains registries, content, planning mirrors, and generated evidence; split by authority. |
| `diag` | `runtime/diagnostics` | `move` | `false` | `false` | `completed` | `CONVERGE-07` | `medium` | Completed in CONVERGE-07; root-level diag/ moved under runtime/diagnostics/. |
| `diagnostics` | `runtime/diagnostics` | `review_absent` | `false` | `false` | `completed` | `CONVERGE-07` | `low` | Confirmed absent in CONVERGE-07; future source material belongs under runtime/diagnostics/. |
| `diegetics` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | contracts/schemas/diegetics; contracts/registries/diegetics; game/domains/diegetics; content/domain-data/diegetics; docs/domains/diegetics; tests/determinism... |
| `dist` | `generated distribution output; future distribution contract review` | `ignore_generated` | `false` | `false` | `not_started` | `review` | `review` | Distribution output is governed by distribution contracts, not source repo layout. |
| `docs` | `docs` | `keep` | `false` | `false` | `not_started` | `none` | `low` | Human-readable doctrine, guides, audits, and explanatory material. |
| `DOMINIUM.md` | `DOMINIUM.md` | `retain_file` | `false` | `false` | `not_started` | `none` | `low` | Allowed root file. |
| `electric` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | contracts/schemas/electric; contracts/registries/electric; game/domains/electric; content/domain-data/electric; docs/domains/electric; tests/determinism/elec... |
| `embodiment` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | contracts/schemas/embodiment; contracts/registries/embodiment; game/domains/embodiment; content/domain-data/embodiment; docs/domains/embodiment; tests/determ... |
| `engine` | `engine` | `keep` | `false` | `false` | `not_started` | `none` | `low` | Deterministic Domino substrate and public engine contracts. |
| `epistemics` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | contracts/schemas/epistemics; contracts/registries/epistemics; game/domains/epistemics; content/domain-data/epistemics; docs/domains/epistemics; tests/determ... |
| `field` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | contracts/schemas/field; contracts/registries/field; game/domains/field; content/domain-data/field; docs/domains/field; tests/determinism/field; tests/fixtur... |
| `fields` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | contracts/schemas/fields; contracts/registries/fields; game/domains/fields; content/domain-data/fields; docs/domains/fields; tests/determinism/fields; tests/... |
| `fluid` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | contracts/schemas/fluid; contracts/registries/fluid; game/domains/fluid; content/domain-data/fluid; docs/domains/fluid; tests/determinism/fluid; tests/fixtur... |
| `game` | `game` | `keep` | `false` | `false` | `not_started` | `none` | `low` | Dominium rules, domain process semantics, and authoritative game meaning. |
| `geo` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | contracts/schemas/geo; contracts/registries/geo; game/domains/geo; content/domain-data/geo; docs/domains/geo; tests/determinism/geo; tests/fixtures/geo |
| `governance` | `docs/governance` | `review` | `false` | `false` | `review` | `review` | `review` | Governance mirrors must not compete with AGENTS.md or canon. |
| `GOVERNANCE.md` | `GOVERNANCE.md` | `retain_file` | `false` | `false` | `not_started` | `none` | `low` | Allowed root file. |
| `ide` | `cmake_or_tools_review` | `review` | `false` | `false` | `review` | `review` | `review` | IDE projections may belong under cmake, tools, or generated evidence depending on role. |
| `infrastructure` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | contracts/schemas/infrastructure; contracts/registries/infrastructure; game/domains/infrastructure; content/domain-data/infrastructure; docs/domains/infrastr... |
| `input` | `runtime/input` | `review_absent` | `false` | `false` | `completed` | `CONVERGE-07` | `low` | Confirmed absent in CONVERGE-07; future source material belongs under runtime/input/. |
| `inspection` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | contracts/schemas/inspection; contracts/registries/inspection; game/domains/inspection; content/domain-data/inspection; docs/domains/inspection; tests/determ... |
| `interaction` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | contracts/schemas/interaction; contracts/registries/interaction; game/domains/interaction; content/domain-data/interaction; docs/domains/interaction; tests/d... |
| `interior` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | contracts/schemas/interior; contracts/registries/interior; game/domains/interior; content/domain-data/interior; docs/domains/interior; tests/determinism/inte... |
| `labs` | `review` | `review` | `false` | `false` | `review` | `review` | `review` | Experimental material requires review before binding. |
| `launcher` | `apps/launcher` | `move` | `false` | `false` | `completed` | `CONVERGE-08` | `medium` | Completed in CONVERGE-08; root-level launcher/ moved under apps/launcher/. |
| `legacy` | `archive/legacy` | `archive` | `false` | `false` | `completed` | `CONVERGE-05` | `low` | Completed in CONVERGE-05; root-level legacy/ moved under archive/legacy/. |
| `lib` | `review` | `review` | `false` | `true` | `review` | `CONVERGE-06` | `review` | Do not classify by name alone; inspect ownership first. |
| `libs` | `review` | `review` | `false` | `true` | `review` | `CONVERGE-06` | `review` | Do not classify by name alone; inspect ownership first. |
| `LICENSE.md` | `LICENSE.md` | `retain_file` | `false` | `false` | `not_started` | `none` | `low` | Allowed root file. |
| `locks` | `contracts/locks_or_store_locks_review` | `review` | `true` | `true` | `review` | `CONVERGE-06` | `review` | Root-level locks/ remains review because it contains concrete deterministic pack lock artifacts, not only lockfile schemas. |
| `logic` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | contracts/schemas/logic; contracts/registries/logic; game/domains/logic; content/domain-data/logic; docs/domains/logic; tests/determinism/logic; tests/fixtur... |
| `logistics` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | contracts/schemas/logistics; contracts/registries/logistics; game/domains/logistics; content/domain-data/logistics; docs/domains/logistics; tests/determinism... |
| `machines` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | contracts/schemas/machines; contracts/registries/machines; game/domains/machines; content/domain-data/machines; docs/domains/machines; tests/determinism/mach... |
| `materials` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | contracts/schemas/materials; contracts/registries/materials; game/domains/materials; content/domain-data/materials; docs/domains/materials; tests/determinism... |
| `mechanics` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | contracts/schemas/mechanics; contracts/registries/mechanics; game/domains/mechanics; content/domain-data/mechanics; docs/domains/mechanics; tests/determinism... |
| `meta` | `review` | `review` | `false` | `false` | `review` | `review` | `review` | Meta surfaces require ownership review. |
| `meta_extensions_engine.py` | `review` | `review` | `false` | `false` | `review` | `review` | `review` | No matching root classification in layout contract. |
| `mobility` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | contracts/schemas/mobility; contracts/registries/mobility; game/domains/mobility; content/domain-data/mobility; docs/domains/mobility; tests/determinism/mobi... |
| `modding` | `content/modding` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | Modding may include content, contracts, and docs. |
| `MODDING.md` | `MODDING.md` | `retain_file` | `false` | `false` | `not_started` | `none` | `low` | Allowed root file. |
| `models` | `content/models` | `move` | `false` | `false` | `not_started` | `CONVERGE-09` | `medium` | Model data should be distinguished from generated or runtime state. |
| `net` | `runtime/network` | `split` | `true` | `true` | `not_started` | `CONVERGE-07` | `high` | Root-level net/ remains mixed after CONVERGE-07 because it contains transport, anti-cheat, SRZ, and server-authoritative policy code; do not move wholesale. |
| `network` | `runtime/network` | `review_absent` | `false` | `false` | `completed` | `CONVERGE-07` | `low` | Confirmed absent in CONVERGE-07; future source material belongs under runtime/network/. |
| `numeric_discipline.py` | `review` | `review` | `false` | `false` | `review` | `review` | `review` | No matching root classification in layout contract. |
| `out` | `generated build output` | `ignore_generated` | `false` | `false` | `not_started` | `review` | `review` | Must not be treated as source repository ownership. |
| `packs` | `content/packs` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | Current runtime pack substrate; pack ownership split remains review-sensitive. |
| `performance` | `tools/performance` | `review` | `false` | `false` | `review` | `review` | `review` | Performance tooling and evidence should stay tool/evidence scoped. |
| `physics` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | contracts/schemas/physics; contracts/registries/physics; game/domains/physics; content/domain-data/physics; docs/domains/physics; tests/determinism/physics; ... |
| `platform` | `runtime/platform` | `review_absent` | `false` | `false` | `completed` | `CONVERGE-07` | `low` | Confirmed absent in CONVERGE-07; future source material belongs under runtime/platform/. |
| `pollution` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | contracts/schemas/pollution; contracts/registries/pollution; game/domains/pollution; content/domain-data/pollution; docs/domains/pollution; tests/determinism... |
| `process` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | contracts/schemas/process; contracts/registries/process; game/domains/process; content/domain-data/process; docs/domains/process; tests/determinism/process; ... |
| `profiles` | `content/profiles` | `move` | `false` | `false` | `not_started` | `CONVERGE-09` | `medium` | Profile data belongs under content unless runtime-store evidence proves otherwise. |
| `quarantine` | `archive/quarantine` | `archive` | `false` | `false` | `completed` | `CONVERGE-05` | `low` | Completed in CONVERGE-05; root-level quarantine/ moved under archive/quarantine/. |
| `README.md` | `README.md` | `retain_file` | `false` | `false` | `not_started` | `none` | `low` | Allowed root file. |
| `reality` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | contracts/schemas/reality; contracts/registries/reality; game/domains/reality; content/domain-data/reality; docs/domains/reality; tests/determinism/reality; ... |
| `registries` | `contracts/registries` | `review_absent` | `false` | `false` | `completed` | `CONVERGE-06` | `low` | Confirmed absent in CONVERGE-06; future registry contracts belong under contracts/registries/. |
| `registry` | `contracts/registries` | `review_absent` | `false` | `false` | `completed` | `CONVERGE-06` | `low` | Confirmed absent in CONVERGE-06; future registry contracts belong under contracts/registries/. |
| `release` | `release` | `keep` | `false` | `false` | `not_started` | `none` | `low` | Release definitions, package recipes, matrices, signing metadata, and release policy inputs. |
| `render` | `runtime/render` | `review_absent` | `false` | `false` | `completed` | `CONVERGE-07` | `low` | Confirmed absent in CONVERGE-07; future source material belongs under runtime/render/. |
| `repo` | `split_to_contracts_docs_tools` | `split` | `true` | `true` | `not_started` | `CONVERGE-06` | `high` | Do not add new authority here; split later into contracts/repo, docs/repo, or tools/migration. |
| `runtime` | `runtime` | `keep` | `false` | `false` | `not_started` | `none` | `medium` | Runtime host, AppShell, platform, render, input, audio, network, storage, diagnostics, and UI adapters. Present canonical target root; inspect contents befor... |
| `safety` | `contracts/safety` | `split` | `true` | `false` | `not_started` | `CONVERGE-06` | `high` | Safety policy belongs under contracts or docs depending on authority. |
| `schema` | `contracts/schemas` | `merge` | `false` | `false` | `completed` | `CONVERGE-06` | `medium` | Completed in CONVERGE-06; root-level schema/ moved under contracts/schemas/. |
| `schemas` | `contracts/schemas` | `merge` | `false` | `false` | `completed` | `CONVERGE-06` | `medium` | Completed in CONVERGE-06; root-level schemas/ merged under contracts/schemas/. |
| `scripts` | `scripts` | `keep` | `false` | `false` | `not_started` | `none` | `low` | Developer workflow scripts and repository automation entrypoints. |
| `security` | `contracts/security` | `split` | `true` | `false` | `not_started` | `CONVERGE-06` | `high` | Security and trust surfaces are protected and review-sensitive. |
| `SECURITY.md` | `SECURITY.md` | `retain_file` | `false` | `false` | `not_started` | `none` | `low` | Allowed root file. |
| `server` | `apps/server` | `move` | `false` | `false` | `completed` | `CONVERGE-08` | `medium` | Completed in CONVERGE-08; root-level server/ moved under apps/server/. |
| `setup` | `apps/setup` | `move` | `false` | `false` | `completed` | `CONVERGE-08` | `medium` | Completed in CONVERGE-08; root-level setup/ moved under apps/setup/. |
| `signals` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | contracts/schemas/signals; contracts/registries/signals; game/domains/signals; content/domain-data/signals; docs/domains/signals; tests/determinism/signals; ... |
| `sitecustomize.py` | `sitecustomize.py` | `retain_file` | `false` | `false` | `not_started` | `none` | `low` | Allowed root file. |
| `specs` | `contracts/specs` | `split` | `true` | `false` | `not_started` | `CONVERGE-06` | `high` | Normative specs must retain authority; reality specs remain canonical over data projections. |
| `storage` | `runtime/storage` | `review_absent` | `false` | `false` | `completed` | `CONVERGE-07` | `low` | Confirmed absent in CONVERGE-07; future source material belongs under runtime/storage/. |
| `system` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | contracts/schemas/system; contracts/registries/system; game/domains/system; content/domain-data/system; docs/domains/system; tests/determinism/system; tests/... |
| `templates` | `content/templates` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | Templates may be authored content, contracts, or generated inputs. |
| `tests` | `tests` | `keep` | `false` | `false` | `not_started` | `none` | `low` | Test suites, determinism checks, fixtures, and verification evidence inputs. |
| `thermal` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | contracts/schemas/thermal; contracts/registries/thermal; game/domains/thermal; content/domain-data/thermal; docs/domains/thermal; tests/determinism/thermal; ... |
| `tool_ui_bind.cmd` | `review` | `review` | `false` | `false` | `review` | `review` | `review` | No matching root classification in layout contract. |
| `tool_ui_doc_annotate.cmd` | `review` | `review` | `false` | `false` | `review` | `review` | `review` | No matching root classification in layout contract. |
| `tool_ui_validate.cmd` | `review` | `review` | `false` | `false` | `review` | `review` | `review` | No matching root classification in layout contract. |
| `tools` | `tools` | `keep` | `false` | `false` | `not_started` | `none` | `low` | Developer, validation, migration, CI, code generation, review, and audit tools. |
| `ui` | `runtime/ui` | `move` | `false` | `false` | `completed` | `CONVERGE-07` | `medium` | Completed in CONVERGE-07; root-level ui/ moved under runtime/ui/. |
| `universe` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | contracts/schemas/universe; contracts/registries/universe; game/domains/universe; content/domain-data/universe; docs/domains/universe; tests/determinism/univ... |
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
| `worldgen` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | contracts/schemas/worldgen; contracts/registries/worldgen; game/domains/worldgen; content/domain-data/worldgen; docs/domains/worldgen; tests/determinism/worl... |
