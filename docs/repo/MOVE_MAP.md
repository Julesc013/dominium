# Move Map

Status: PROVISIONAL
Phase: CONVERGE-07
Machine-readable source: `tools/migration/root_move_map.json`

This document explains the generated move map. The map is a planning artifact: it records completed and future moves, but it does not execute moves by itself.

## CONVERGE-07 Note

CONVERGE-07 completed runtime-facing convergence for root-level `app/`, `appshell/`, `ui/`, and `diag/`. `net/`, `control/`, and `core/` remain split/review entries because they are mixed or ownership-sensitive. Product roots remain for CONVERGE-08 and domain roots remain for CONVERGE-09.

Future migration sequence:

- CONVERGE-08 product entrypoints into `apps/`
- CONVERGE-09 domain split into contracts/game/content/docs/tests
- CONVERGE-10 blocking validation after controlled moves
- CONVERGE-11 product/platform/render/native/toolchain/package matrices

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
| `app` | `runtime/app` | `move` | `false` | `false` | `completed` | `CONVERGE-07` | `medium` | Root-level app/ is retired; retained app runtime substrate lives under runtime/app/. |
| `appshell` | `runtime/appshell` | `move` | `false` | `false` | `completed` | `CONVERGE-07` | `medium` | Root-level appshell/ is retired; AppShell source lives under runtime/appshell/. |
| `archive` | `archive` | `keep` | `false` | `false` | `not_started` | `none` | `low` | Historical, superseded, quarantined, generated-evidence, and legacy material retained with provenance. |
| `artifacts` | `generated evidence or release artifact review` | `ignore_generated` | `false` | `false` | `not_started` | `review` | `review` | Review before using as authority. |
| `astro` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | contracts/schemas/astro; contracts/registries/astro; game/domains/astro; content/domain-data/astro; docs/domains/astro; tests/determinism... |
| `attic` | `archive/historical/attic` | `archive` | `false` | `false` | `completed` | `CONVERGE-05` | `low` | Root-level attic/ is retired; material is retained under archive/historical/attic/. |
| `audio` | `runtime/audio` | `review_absent` | `false` | `false` | `completed` | `CONVERGE-07` | `low` | Root-level audio/ was not present during CONVERGE-07. |
| `bundles` | `content_or_exports_review` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | Authored bundles and generated exports require separate handling. |
| `CHANGELOG.md` | `CHANGELOG.md` | `retain_file` | `false` | `false` | `not_started` | `none` | `low` | Allowed root file. |
| `chem` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | contracts/schemas/chem; contracts/registries/chem; game/domains/chem; content/domain-data/chem; docs/domains/chem; tests/determinism/chem... |
| `CLAUDE.md` | `CLAUDE.md` | `retain_file` | `false` | `false` | `not_started` | `none` | `low` | Allowed root file. |
| `client` | `apps/client` | `move` | `false` | `true` | `not_started` | `CONVERGE-08` | `medium` | Only thin product binding should remain under apps. |
| `cmake` | `cmake` | `keep` | `false` | `false` | `not_started` | `none` | `low` | CMake modules and build configuration helpers. |
| `CMakeLists.txt` | `CMakeLists.txt` | `retain_file` | `false` | `false` | `not_started` | `none` | `low` | Allowed root file. |
| `CMakePresets.json` | `CMakePresets.json` | `retain_file` | `false` | `false` | `not_started` | `none` | `low` | Allowed root file. |
| `CODE_CHANGE_JUSTIFICATION.md` | `CODE_CHANGE_JUSTIFICATION.md` | `retain_file` | `false` | `false` | `not_started` | `none` | `low` | Allowed root file. |
| `compat` | `contracts/compatibility_plus_runtime_review` | `review` | `true` | `true` | `review` | `CONVERGE-06` | `review` | Root-level compat/ remains mixed implementation and shim code after CONVERGE-06; do not move wholesale into contracts/. |
| `contracts` | `contracts` | `keep` | `false` | `false` | `not_started` | `none` | `low` | Machine-readable and prose contracts for schemas, registries, protocols, compatibility, stability, replay, ABI, repository, and distribut... |
| `CONTRIBUTING.md` | `CONTRIBUTING.md` | `retain_file` | `false` | `false` | `not_started` | `none` | `low` | Allowed root file. |
| `control` | `runtime/control` | `split` | `true` | `true` | `not_started` | `CONVERGE-07` | `high` | Control substrate must preserve process-only mutation boundaries. |
| `core` | `runtime/core_or_game_domain_review` | `split` | `true` | `true` | `not_started` | `CONVERGE-07` | `high` | Core is likely mixed; do not move wholesale. |
| `data` | `content_or_runtime_store_review` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | Data contains registries, content, planning mirrors, and generated evidence; split by authority. |
| `diag` | `runtime/diagnostics` | `move` | `false` | `false` | `completed` | `CONVERGE-07` | `medium` | Root-level diag/ is retired; source diagnostics live under runtime/diagnostics/. |
| `diagnostics` | `runtime/diagnostics` | `review_absent` | `false` | `false` | `completed` | `CONVERGE-07` | `low` | Root-level diagnostics/ was not present during CONVERGE-07. |
| `diegetics` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | contracts/schemas/diegetics; contracts/registries/diegetics; game/domains/diegetics; content/domain-data/diegetics; docs/domains/diegetic... |
| `dist` | `generated distribution output; future distribution contract review` | `ignore_generated` | `false` | `false` | `not_started` | `review` | `review` | Distribution output is governed by distribution contracts, not source repo layout. |
| `docs` | `docs` | `keep` | `false` | `false` | `not_started` | `none` | `low` | Human-readable doctrine, guides, audits, and explanatory material. |
| `DOMINIUM.md` | `DOMINIUM.md` | `retain_file` | `false` | `false` | `not_started` | `none` | `low` | Allowed root file. |
| `electric` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | contracts/schemas/electric; contracts/registries/electric; game/domains/electric; content/domain-data/electric; docs/domains/electric; te... |
| `embodiment` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | contracts/schemas/embodiment; contracts/registries/embodiment; game/domains/embodiment; content/domain-data/embodiment; docs/domains/embo... |
| `engine` | `engine` | `keep` | `false` | `false` | `not_started` | `none` | `low` | Deterministic Domino substrate and public engine contracts. |
| `epistemics` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | contracts/schemas/epistemics; contracts/registries/epistemics; game/domains/epistemics; content/domain-data/epistemics; docs/domains/epis... |
| `field` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | contracts/schemas/field; contracts/registries/field; game/domains/field; content/domain-data/field; docs/domains/field; tests/determinism... |
| `fields` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | contracts/schemas/fields; contracts/registries/fields; game/domains/fields; content/domain-data/fields; docs/domains/fields; tests/determ... |
| `fluid` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | contracts/schemas/fluid; contracts/registries/fluid; game/domains/fluid; content/domain-data/fluid; docs/domains/fluid; tests/determinism... |
| `game` | `game` | `keep` | `false` | `false` | `not_started` | `none` | `low` | Dominium rules, domain process semantics, and authoritative game meaning. |
| `geo` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | contracts/schemas/geo; contracts/registries/geo; game/domains/geo; content/domain-data/geo; docs/domains/geo; tests/determinism/geo; test... |
| `governance` | `docs/governance` | `review` | `false` | `false` | `review` | `review` | `review` | Governance mirrors must not compete with AGENTS.md or canon. |
| `GOVERNANCE.md` | `GOVERNANCE.md` | `retain_file` | `false` | `false` | `not_started` | `none` | `low` | Allowed root file. |
| `ide` | `cmake_or_tools_review` | `review` | `false` | `false` | `review` | `review` | `review` | IDE projections may belong under cmake, tools, or generated evidence depending on role. |
| `infrastructure` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | contracts/schemas/infrastructure; contracts/registries/infrastructure; game/domains/infrastructure; content/domain-data/infrastructure; d... |
| `input` | `runtime/input` | `review_absent` | `false` | `false` | `completed` | `CONVERGE-07` | `low` | Root-level input/ was not present during CONVERGE-07. |
| `inspection` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | contracts/schemas/inspection; contracts/registries/inspection; game/domains/inspection; content/domain-data/inspection; docs/domains/insp... |
| `interaction` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | contracts/schemas/interaction; contracts/registries/interaction; game/domains/interaction; content/domain-data/interaction; docs/domains/... |
| `interior` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | contracts/schemas/interior; contracts/registries/interior; game/domains/interior; content/domain-data/interior; docs/domains/interior; te... |
| `labs` | `review` | `review` | `false` | `false` | `review` | `review` | `review` | Experimental material requires review before binding. |
| `launcher` | `apps/launcher` | `move` | `false` | `true` | `not_started` | `CONVERGE-08` | `medium` | Launcher product identity and executable naming must remain stable. |
| `legacy` | `archive/legacy` | `archive` | `false` | `false` | `completed` | `CONVERGE-05` | `low` | Root-level legacy/ is retired; material is retained under archive/legacy/. |
| `lib` | `review` | `review` | `false` | `true` | `review` | `CONVERGE-06` | `review` | Do not classify by name alone; inspect ownership first. |
| `libs` | `review` | `review` | `false` | `true` | `review` | `CONVERGE-06` | `review` | Do not classify by name alone; inspect ownership first. |
| `LICENSE.md` | `LICENSE.md` | `retain_file` | `false` | `false` | `not_started` | `none` | `low` | Allowed root file. |
| `locks` | `contracts/locks_or_store_locks_review` | `review` | `true` | `true` | `review` | `CONVERGE-06` | `review` | Root-level locks/ remains review because it contains concrete deterministic pack lock artifacts, not only lockfile schemas. |
| `logic` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | contracts/schemas/logic; contracts/registries/logic; game/domains/logic; content/domain-data/logic; docs/domains/logic; tests/determinism... |
| `logistics` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | contracts/schemas/logistics; contracts/registries/logistics; game/domains/logistics; content/domain-data/logistics; docs/domains/logistic... |
| `machines` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | contracts/schemas/machines; contracts/registries/machines; game/domains/machines; content/domain-data/machines; docs/domains/machines; te... |
| `materials` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | contracts/schemas/materials; contracts/registries/materials; game/domains/materials; content/domain-data/materials; docs/domains/material... |
| `mechanics` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | contracts/schemas/mechanics; contracts/registries/mechanics; game/domains/mechanics; content/domain-data/mechanics; docs/domains/mechanic... |
| `meta` | `review` | `review` | `false` | `false` | `review` | `review` | `review` | Meta surfaces require ownership review. |
| `meta_extensions_engine.py` | `review` | `review` | `false` | `false` | `review` | `review` | `review` | No matching root classification in layout contract. |
| `mobility` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | contracts/schemas/mobility; contracts/registries/mobility; game/domains/mobility; content/domain-data/mobility; docs/domains/mobility; te... |
| `modding` | `content/modding` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | Modding may include content, contracts, and docs. |
| `MODDING.md` | `MODDING.md` | `retain_file` | `false` | `false` | `not_started` | `none` | `low` | Allowed root file. |
| `models` | `content/models` | `move` | `false` | `false` | `not_started` | `CONVERGE-09` | `medium` | Model data should be distinguished from generated or runtime state. |
| `net` | `runtime/network` | `split` | `true` | `true` | `not_started` | `CONVERGE-07` | `high` | Root-level net/ remains mixed after CONVERGE-07 because it contains transport, anti-cheat, SRZ, and server-authoritative policy code; do... |
| `network` | `runtime/network` | `review_absent` | `false` | `false` | `completed` | `CONVERGE-07` | `low` | Root-level network/ was not present during CONVERGE-07. |
| `numeric_discipline.py` | `review` | `review` | `false` | `false` | `review` | `review` | `review` | No matching root classification in layout contract. |
| `packs` | `content/packs` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | Current runtime pack substrate; pack ownership split remains review-sensitive. |
| `performance` | `tools/performance` | `review` | `false` | `false` | `review` | `review` | `review` | Performance tooling and evidence should stay tool/evidence scoped. |
| `physics` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | contracts/schemas/physics; contracts/registries/physics; game/domains/physics; content/domain-data/physics; docs/domains/physics; tests/d... |
| `platform` | `runtime/platform` | `review_absent` | `false` | `false` | `completed` | `CONVERGE-07` | `low` | Root-level platform/ was not present during CONVERGE-07. |
| `pollution` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | contracts/schemas/pollution; contracts/registries/pollution; game/domains/pollution; content/domain-data/pollution; docs/domains/pollutio... |
| `process` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | contracts/schemas/process; contracts/registries/process; game/domains/process; content/domain-data/process; docs/domains/process; tests/d... |
| `profiles` | `content/profiles` | `move` | `false` | `false` | `not_started` | `CONVERGE-09` | `medium` | Profile data belongs under content unless runtime-store evidence proves otherwise. |
| `quarantine` | `archive/quarantine` | `archive` | `false` | `false` | `completed` | `CONVERGE-05` | `low` | Root-level quarantine/ is retired; material is retained under archive/quarantine/. |
| `README.md` | `README.md` | `retain_file` | `false` | `false` | `not_started` | `none` | `low` | Allowed root file. |
| `reality` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | contracts/schemas/reality; contracts/registries/reality; game/domains/reality; content/domain-data/reality; docs/domains/reality; tests/d... |
| `registries` | `contracts/registries` | `review_absent` | `false` | `false` | `completed` | `CONVERGE-06` | `low` | Root-level registries/ was not present during CONVERGE-06. |
| `registry` | `contracts/registries` | `review_absent` | `false` | `false` | `completed` | `CONVERGE-06` | `low` | Root-level registry/ was not present during CONVERGE-06. |
| `release` | `release` | `keep` | `false` | `false` | `not_started` | `none` | `low` | Release definitions, package recipes, matrices, signing metadata, and release policy inputs. |
| `render` | `runtime/render` | `review_absent` | `false` | `false` | `completed` | `CONVERGE-07` | `low` | Root-level render/ was not present during CONVERGE-07. |
| `repo` | `split_to_contracts_docs_tools` | `split` | `true` | `true` | `not_started` | `CONVERGE-06` | `high` | Do not add new authority here; split later into contracts/repo, docs/repo, or tools/migration. |
| `runtime` | `runtime` | `keep` | `false` | `false` | `not_started` | `none` | `medium` | Runtime host, AppShell, platform, render, input, audio, network, storage, diagnostics, and UI adapters. Present canonical target root; in... |
| `safety` | `contracts/safety` | `split` | `true` | `false` | `not_started` | `CONVERGE-06` | `high` | Safety policy belongs under contracts or docs depending on authority. |
| `schema` | `contracts/schemas` | `merge` | `false` | `false` | `completed` | `CONVERGE-06` | `medium` | Root-level schema/ is retired; retained schema law lives under contracts/schemas/. |
| `schemas` | `contracts/schemas` | `merge` | `false` | `false` | `completed` | `CONVERGE-06` | `medium` | Root-level schemas/ is retired; retained validator-facing schema projections live under contracts/schemas/. |
| `scripts` | `scripts` | `keep` | `false` | `false` | `not_started` | `none` | `low` | Developer workflow scripts and repository automation entrypoints. |
| `security` | `contracts/security` | `split` | `true` | `false` | `not_started` | `CONVERGE-06` | `high` | Security and trust surfaces are protected and review-sensitive. |
| `SECURITY.md` | `SECURITY.md` | `retain_file` | `false` | `false` | `not_started` | `none` | `low` | Allowed root file. |
| `server` | `apps/server` | `move` | `false` | `true` | `not_started` | `CONVERGE-08` | `medium` | Server authority semantics must stay governed by game/engine/runtime contracts. |
| `setup` | `apps/setup` | `move` | `false` | `true` | `not_started` | `CONVERGE-08` | `medium` | Setup install identity and virtual roots must not change during moves. |
| `signals` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | contracts/schemas/signals; contracts/registries/signals; game/domains/signals; content/domain-data/signals; docs/domains/signals; tests/d... |
| `sitecustomize.py` | `sitecustomize.py` | `retain_file` | `false` | `false` | `not_started` | `none` | `low` | Allowed root file. |
| `specs` | `contracts/specs` | `split` | `true` | `false` | `not_started` | `CONVERGE-06` | `high` | Normative specs must retain authority; reality specs remain canonical over data projections. |
| `storage` | `runtime/storage` | `review_absent` | `false` | `false` | `completed` | `CONVERGE-07` | `low` | Root-level storage/ was not present during CONVERGE-07. |
| `system` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | contracts/schemas/system; contracts/registries/system; game/domains/system; content/domain-data/system; docs/domains/system; tests/determ... |
| `templates` | `content/templates` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | Templates may be authored content, contracts, or generated inputs. |
| `tests` | `tests` | `keep` | `false` | `false` | `not_started` | `none` | `low` | Test suites, determinism checks, fixtures, and verification evidence inputs. |
| `thermal` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | contracts/schemas/thermal; contracts/registries/thermal; game/domains/thermal; content/domain-data/thermal; docs/domains/thermal; tests/d... |
| `tool_ui_bind.cmd` | `review` | `review` | `false` | `false` | `review` | `review` | `review` | No matching root classification in layout contract. |
| `tool_ui_doc_annotate.cmd` | `review` | `review` | `false` | `false` | `review` | `review` | `review` | No matching root classification in layout contract. |
| `tool_ui_validate.cmd` | `review` | `review` | `false` | `false` | `review` | `review` | `review` | No matching root classification in layout contract. |
| `tools` | `tools` | `keep` | `false` | `false` | `not_started` | `none` | `low` | Developer, validation, migration, CI, code generation, review, and audit tools. |
| `ui` | `runtime/ui` | `move` | `false` | `false` | `completed` | `CONVERGE-07` | `medium` | Root-level ui/ is retired; shared UI runtime source lives under runtime/ui/. |
| `universe` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | contracts/schemas/universe; contracts/registries/universe; game/domains/universe; content/domain-data/universe; docs/domains/universe; te... |
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
| `worldgen` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `not_started` | `CONVERGE-09` | `high` | contracts/schemas/worldgen; contracts/registries/worldgen; game/domains/worldgen; content/domain-data/worldgen; docs/domains/worldgen; te... |

No moves are executed by this map.
