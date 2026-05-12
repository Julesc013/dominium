# Move Map

Status: PROVISIONAL
Phase: CONVERGE-05
Machine-readable source: `tools/migration/root_move_map.json`

This document explains the generated move map. The map is a planning artifact: it records completed and future moves, but it does not execute moves by itself.

## CONVERGE-05 Note

CONVERGE-05 completed archive-family root convergence. `attic/`, `legacy/`, and `quarantine/` are recorded as completed archive moves and must not be recreated as root-level ownership surfaces.

Future migration sequence:

- CONVERGE-06 contracts/schema/registry/compat convergence
- CONVERGE-07 runtime/AppShell/platform/render/UI convergence
- CONVERGE-08 product entrypoints into `apps/`
- CONVERGE-09 domain split into contracts/game/content/docs/tests

Distribution, install, media, portable-store, package-cache, bundle, and runtime projection layouts are handled by CONVERGE-04, not by this source-repo move map.

## Warnings

- Domain roots must not be moved wholesale unless proven pure.
- Product roots must remain thin after migration.
- Runtime roots must not own simulation truth.
- `dist/`, `build/`, `out/`, package caches, staging directories, media payloads, and runtime stores must not be confused with source ownership roots.

## Planning Table

| Current Path | Proposed Target | Action | Split? | Shim? | Phase | Risk | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `.agentignore` | `.agentignore` | `retain_file` | `false` | `false` | `none` | `low` | Allowed root file. |
| `.aide` | `.aide` | `retain_metadata` | `false` | `false` | `none` | `low` | Allowed metadata/config root. |
| `.aide.local.example` | `.aide.local.example` | `retain_metadata` | `false` | `false` | `none` | `low` | Allowed metadata/config root. |
| `.gitattributes` | `.gitattributes` | `retain_file` | `false` | `false` | `none` | `low` | Allowed root file. |
| `.github` | `.github` | `retain_metadata` | `false` | `false` | `none` | `low` | Allowed metadata/config root. |
| `.gitignore` | `.gitignore` | `retain_file` | `false` | `false` | `none` | `low` | Allowed root file. |
| `.vscode` | `.vscode` | `retain_metadata` | `false` | `false` | `none` | `low` | Allowed metadata/config root. |
| `__init__.py` | `review` | `review` | `false` | `false` | `review` | `review` | No matching root classification in layout contract. |
| `AGENTS.md` | `AGENTS.md` | `retain_file` | `false` | `false` | `none` | `low` | Allowed root file. |
| `app` | `runtime/app` | `move` | `false` | `true` | `CONVERGE-07` | `medium` | Current runtime/app substrate; do not move in CONVERGE-01. |
| `appshell` | `runtime/appshell` | `move` | `false` | `true` | `CONVERGE-07` | `medium` | AppShell should converge under runtime after boundary proof. |
| `archive` | `archive` | `keep` | `false` | `false` | `none` | `low` | Historical, superseded, quarantined, generated-evidence, and legacy material retained with provenance. |
| `artifacts` | `generated evidence or release artifact review` | `ignore_generated` | `false` | `false` | `review` | `review` | Review before using as authority. |
| `astro` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `CONVERGE-09` | `high` | contracts/schemas/astro; contracts/registries/astro; game/domains/astro; content/domain-data/astro; docs/domains/astr... |
| `attic` | `archive/historical/attic` | `archive` | `false` | `false` | `CONVERGE-05` | `low` | COMPLETED: Root-level attic/ is retired; material is retained under archive/historical/attic/. |
| `bundles` | `content_or_exports_review` | `split` | `true` | `false` | `CONVERGE-09` | `high` | Authored bundles and generated exports require separate handling. |
| `CHANGELOG.md` | `CHANGELOG.md` | `retain_file` | `false` | `false` | `none` | `low` | Allowed root file. |
| `chem` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `CONVERGE-09` | `high` | contracts/schemas/chem; contracts/registries/chem; game/domains/chem; content/domain-data/chem; docs/domains/chem; te... |
| `CLAUDE.md` | `CLAUDE.md` | `retain_file` | `false` | `false` | `none` | `low` | Allowed root file. |
| `client` | `apps/client` | `move` | `false` | `true` | `CONVERGE-08` | `medium` | Only thin product binding should remain under apps. |
| `cmake` | `cmake` | `keep` | `false` | `false` | `none` | `low` | CMake modules and build configuration helpers. |
| `CMakeLists.txt` | `CMakeLists.txt` | `retain_file` | `false` | `false` | `none` | `low` | Allowed root file. |
| `CMakePresets.json` | `CMakePresets.json` | `retain_file` | `false` | `false` | `none` | `low` | Allowed root file. |
| `CODE_CHANGE_JUSTIFICATION.md` | `CODE_CHANGE_JUSTIFICATION.md` | `retain_file` | `false` | `false` | `none` | `low` | Allowed root file. |
| `compat` | `contracts/compatibility` | `split` | `true` | `true` | `CONVERGE-06` | `high` | Compatibility meaning belongs in contracts; runtime adapters may move separately. |
| `contracts` | `contracts` | `keep` | `false` | `false` | `none` | `low` | Machine-readable and prose contracts for schemas, registries, protocols, compatibility, stability, replay, ABI, repos... |
| `CONTRIBUTING.md` | `CONTRIBUTING.md` | `retain_file` | `false` | `false` | `none` | `low` | Allowed root file. |
| `control` | `runtime/control` | `split` | `true` | `true` | `CONVERGE-07` | `high` | Control substrate must preserve process-only mutation boundaries. |
| `core` | `runtime/core_or_game_domain_review` | `split` | `true` | `true` | `CONVERGE-07` | `high` | Core is likely mixed; do not move wholesale. |
| `data` | `content_or_runtime_store_review` | `split` | `true` | `false` | `CONVERGE-09` | `high` | Data contains registries, content, planning mirrors, and generated evidence; split by authority. |
| `diag` | `runtime/diagnostics` | `move` | `false` | `true` | `CONVERGE-07` | `medium` | Diagnostics belong under runtime if they do not own truth. |
| `diegetics` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `CONVERGE-09` | `high` | contracts/schemas/diegetics; contracts/registries/diegetics; game/domains/diegetics; content/domain-data/diegetics; d... |
| `dist` | `generated distribution output; future distribution contract review` | `ignore_generated` | `false` | `false` | `review` | `review` | Distribution output is governed by distribution contracts, not source repo layout. |
| `docs` | `docs` | `keep` | `false` | `false` | `none` | `low` | Human-readable doctrine, guides, audits, and explanatory material. |
| `DOMINIUM.md` | `DOMINIUM.md` | `retain_file` | `false` | `false` | `none` | `low` | Allowed root file. |
| `electric` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `CONVERGE-09` | `high` | contracts/schemas/electric; contracts/registries/electric; game/domains/electric; content/domain-data/electric; docs/... |
| `embodiment` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `CONVERGE-09` | `high` | contracts/schemas/embodiment; contracts/registries/embodiment; game/domains/embodiment; content/domain-data/embodimen... |
| `engine` | `engine` | `keep` | `false` | `false` | `none` | `low` | Deterministic Domino substrate and public engine contracts. |
| `epistemics` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `CONVERGE-09` | `high` | contracts/schemas/epistemics; contracts/registries/epistemics; game/domains/epistemics; content/domain-data/epistemic... |
| `field` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `CONVERGE-09` | `high` | contracts/schemas/field; contracts/registries/field; game/domains/field; content/domain-data/field; docs/domains/fiel... |
| `fields` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `CONVERGE-09` | `high` | contracts/schemas/fields; contracts/registries/fields; game/domains/fields; content/domain-data/fields; docs/domains/... |
| `fluid` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `CONVERGE-09` | `high` | contracts/schemas/fluid; contracts/registries/fluid; game/domains/fluid; content/domain-data/fluid; docs/domains/flui... |
| `game` | `game` | `keep` | `false` | `false` | `none` | `low` | Dominium rules, domain process semantics, and authoritative game meaning. |
| `geo` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `CONVERGE-09` | `high` | contracts/schemas/geo; contracts/registries/geo; game/domains/geo; content/domain-data/geo; docs/domains/geo; tests/d... |
| `governance` | `docs/governance` | `review` | `false` | `false` | `review` | `review` | Governance mirrors must not compete with AGENTS.md or canon. |
| `GOVERNANCE.md` | `GOVERNANCE.md` | `retain_file` | `false` | `false` | `none` | `low` | Allowed root file. |
| `ide` | `cmake_or_tools_review` | `review` | `false` | `false` | `review` | `review` | IDE projections may belong under cmake, tools, or generated evidence depending on role. |
| `infrastructure` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `CONVERGE-09` | `high` | contracts/schemas/infrastructure; contracts/registries/infrastructure; game/domains/infrastructure; content/domain-da... |
| `inspection` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `CONVERGE-09` | `high` | contracts/schemas/inspection; contracts/registries/inspection; game/domains/inspection; content/domain-data/inspectio... |
| `interaction` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `CONVERGE-09` | `high` | contracts/schemas/interaction; contracts/registries/interaction; game/domains/interaction; content/domain-data/intera... |
| `interior` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `CONVERGE-09` | `high` | contracts/schemas/interior; contracts/registries/interior; game/domains/interior; content/domain-data/interior; docs/... |
| `labs` | `review` | `review` | `false` | `false` | `review` | `review` | Experimental material requires review before binding. |
| `launcher` | `apps/launcher` | `move` | `false` | `true` | `CONVERGE-08` | `medium` | Launcher product identity and executable naming must remain stable. |
| `legacy` | `archive/legacy` | `archive` | `false` | `false` | `CONVERGE-05` | `low` | COMPLETED: Root-level legacy/ is retired; material is retained under archive/legacy/. |
| `lib` | `review` | `review` | `false` | `true` | `CONVERGE-06` | `review` | Do not classify by name alone; inspect ownership first. |
| `libs` | `review` | `review` | `false` | `true` | `CONVERGE-06` | `review` | Do not classify by name alone; inspect ownership first. |
| `LICENSE.md` | `LICENSE.md` | `retain_file` | `false` | `false` | `none` | `low` | Allowed root file. |
| `locks` | `contracts/replay` | `split` | `true` | `true` | `CONVERGE-06` | `high` | Deterministic locks, runtime locks, and ops transactions require separate homes. |
| `logic` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `CONVERGE-09` | `high` | contracts/schemas/logic; contracts/registries/logic; game/domains/logic; content/domain-data/logic; docs/domains/logi... |
| `logistics` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `CONVERGE-09` | `high` | contracts/schemas/logistics; contracts/registries/logistics; game/domains/logistics; content/domain-data/logistics; d... |
| `machines` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `CONVERGE-09` | `high` | contracts/schemas/machines; contracts/registries/machines; game/domains/machines; content/domain-data/machines; docs/... |
| `materials` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `CONVERGE-09` | `high` | contracts/schemas/materials; contracts/registries/materials; game/domains/materials; content/domain-data/materials; d... |
| `mechanics` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `CONVERGE-09` | `high` | contracts/schemas/mechanics; contracts/registries/mechanics; game/domains/mechanics; content/domain-data/mechanics; d... |
| `meta` | `review` | `review` | `false` | `false` | `review` | `review` | Meta surfaces require ownership review. |
| `meta_extensions_engine.py` | `review` | `review` | `false` | `false` | `review` | `review` | No matching root classification in layout contract. |
| `mobility` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `CONVERGE-09` | `high` | contracts/schemas/mobility; contracts/registries/mobility; game/domains/mobility; content/domain-data/mobility; docs/... |
| `modding` | `content/modding` | `split` | `true` | `false` | `CONVERGE-09` | `high` | Modding may include content, contracts, and docs. |
| `MODDING.md` | `MODDING.md` | `retain_file` | `false` | `false` | `none` | `low` | Allowed root file. |
| `models` | `content/models` | `move` | `false` | `false` | `CONVERGE-09` | `medium` | Model data should be distinguished from generated or runtime state. |
| `net` | `runtime/network` | `move` | `false` | `true` | `CONVERGE-07` | `medium` | Network adapters belong under runtime after authority boundaries are checked. |
| `numeric_discipline.py` | `review` | `review` | `false` | `false` | `review` | `review` | No matching root classification in layout contract. |
| `packs` | `content/packs` | `split` | `true` | `false` | `CONVERGE-09` | `high` | Current runtime pack substrate; pack ownership split remains review-sensitive. |
| `performance` | `tools/performance` | `review` | `false` | `false` | `review` | `review` | Performance tooling and evidence should stay tool/evidence scoped. |
| `physics` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `CONVERGE-09` | `high` | contracts/schemas/physics; contracts/registries/physics; game/domains/physics; content/domain-data/physics; docs/doma... |
| `pollution` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `CONVERGE-09` | `high` | contracts/schemas/pollution; contracts/registries/pollution; game/domains/pollution; content/domain-data/pollution; d... |
| `process` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `CONVERGE-09` | `high` | contracts/schemas/process; contracts/registries/process; game/domains/process; content/domain-data/process; docs/doma... |
| `profiles` | `content/profiles` | `move` | `false` | `false` | `CONVERGE-09` | `medium` | Profile data belongs under content unless runtime-store evidence proves otherwise. |
| `quarantine` | `archive/quarantine` | `archive` | `false` | `false` | `CONVERGE-05` | `low` | COMPLETED: Root-level quarantine/ is retired; material is retained under archive/quarantine/. |
| `README.md` | `README.md` | `retain_file` | `false` | `false` | `none` | `low` | Allowed root file. |
| `reality` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `CONVERGE-09` | `high` | contracts/schemas/reality; contracts/registries/reality; game/domains/reality; content/domain-data/reality; docs/doma... |
| `release` | `release` | `keep` | `false` | `false` | `none` | `low` | Release definitions, package recipes, matrices, signing metadata, and release policy inputs. |
| `repo` | `split_to_contracts_docs_tools` | `split` | `true` | `true` | `CONVERGE-06` | `high` | Do not add new authority here; split later into contracts/repo, docs/repo, or tools/migration. |
| `runtime` | `runtime` | `keep` | `false` | `false` | `none` | `medium` | Runtime host, AppShell, platform, render, input, audio, network, storage, diagnostics, and UI adapters. Present canon... |
| `safety` | `contracts/safety` | `split` | `true` | `false` | `CONVERGE-06` | `high` | Safety policy belongs under contracts or docs depending on authority. |
| `schema` | `contracts/schemas` | `merge` | `false` | `true` | `CONVERGE-06` | `high` | Current canonical schema law root; future physical convergence must preserve semantic authority. |
| `schemas` | `contracts/schemas` | `merge` | `false` | `true` | `CONVERGE-06` | `high` | Current validator-facing schema projection; must not replace schema law silently. |
| `scripts` | `scripts` | `keep` | `false` | `false` | `none` | `low` | Developer workflow scripts and repository automation entrypoints. |
| `security` | `contracts/security` | `split` | `true` | `false` | `CONVERGE-06` | `high` | Security and trust surfaces are protected and review-sensitive. |
| `SECURITY.md` | `SECURITY.md` | `retain_file` | `false` | `false` | `none` | `low` | Allowed root file. |
| `server` | `apps/server` | `move` | `false` | `true` | `CONVERGE-08` | `medium` | Server authority semantics must stay governed by game/engine/runtime contracts. |
| `setup` | `apps/setup` | `move` | `false` | `true` | `CONVERGE-08` | `medium` | Setup install identity and virtual roots must not change during moves. |
| `signals` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `CONVERGE-09` | `high` | contracts/schemas/signals; contracts/registries/signals; game/domains/signals; content/domain-data/signals; docs/doma... |
| `sitecustomize.py` | `sitecustomize.py` | `retain_file` | `false` | `false` | `none` | `low` | Allowed root file. |
| `specs` | `contracts/specs` | `split` | `true` | `false` | `CONVERGE-06` | `high` | Normative specs must retain authority; reality specs remain canonical over data projections. |
| `system` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `CONVERGE-09` | `high` | contracts/schemas/system; contracts/registries/system; game/domains/system; content/domain-data/system; docs/domains/... |
| `templates` | `content/templates` | `split` | `true` | `false` | `CONVERGE-09` | `high` | Templates may be authored content, contracts, or generated inputs. |
| `tests` | `tests` | `keep` | `false` | `false` | `none` | `low` | Test suites, determinism checks, fixtures, and verification evidence inputs. |
| `thermal` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `CONVERGE-09` | `high` | contracts/schemas/thermal; contracts/registries/thermal; game/domains/thermal; content/domain-data/thermal; docs/doma... |
| `tool_ui_bind.cmd` | `review` | `review` | `false` | `false` | `review` | `review` | No matching root classification in layout contract. |
| `tool_ui_doc_annotate.cmd` | `review` | `review` | `false` | `false` | `review` | `review` | No matching root classification in layout contract. |
| `tool_ui_validate.cmd` | `review` | `review` | `false` | `false` | `review` | `review` | No matching root classification in layout contract. |
| `tools` | `tools` | `keep` | `false` | `false` | `none` | `low` | Developer, validation, migration, CI, code generation, review, and audit tools. |
| `ui` | `runtime/ui` | `move` | `false` | `true` | `CONVERGE-07` | `medium` | UI is presentation/adaptation only and must not mutate truth. |
| `universe` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `CONVERGE-09` | `high` | contracts/schemas/universe; contracts/registries/universe; game/domains/universe; content/domain-data/universe; docs/... |
| `updates` | `release_or_ops_review` | `split` | `true` | `false` | `review` | `high` | Update metadata belongs to release/control-plane ownership after review. |
| `validation` | `tools/validation` | `review` | `false` | `false` | `review` | `review` | Validation tooling belongs under tools unless it is contract law. |
| `VERSION_CLIENT` | `VERSION_CLIENT` | `retain_file` | `false` | `false` | `none` | `low` | Allowed root file. |
| `VERSION_ENGINE` | `VERSION_ENGINE` | `retain_file` | `false` | `false` | `none` | `low` | Allowed root file. |
| `VERSION_GAME` | `VERSION_GAME` | `retain_file` | `false` | `false` | `none` | `low` | Allowed root file. |
| `VERSION_LAUNCHER` | `VERSION_LAUNCHER` | `retain_file` | `false` | `false` | `none` | `low` | Allowed root file. |
| `VERSION_SERVER` | `VERSION_SERVER` | `retain_file` | `false` | `false` | `none` | `low` | Allowed root file. |
| `VERSION_SETUP` | `VERSION_SETUP` | `retain_file` | `false` | `false` | `none` | `low` | Allowed root file. |
| `VERSION_SUITE` | `VERSION_SUITE` | `retain_file` | `false` | `false` | `none` | `low` | Allowed root file. |
| `VERSION_TOOLS` | `VERSION_TOOLS` | `retain_file` | `false` | `false` | `none` | `low` | Allowed root file. |
| `worldgen` | `contracts/game/content/docs/tests split` | `split` | `true` | `false` | `CONVERGE-09` | `high` | contracts/schemas/worldgen; contracts/registries/worldgen; game/domains/worldgen; content/domain-data/worldgen; docs/... |

No product, runtime, schema, contract, content, generated-output, or domain root moves were performed in CONVERGE-05.
