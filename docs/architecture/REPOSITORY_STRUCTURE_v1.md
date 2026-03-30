Status: DERIVED
Last Reviewed: 2026-03-30
Stability: stable
Future Series: XI-8
Replacement Target: superseded only by a later explicit repository-structure lock revision

# Repository Structure v1

Xi-8 freezes the live repository structure as it exists after Xi-5x2, Xi-6, and Xi-7.

- repository structure lock hash: `f419ce454578b60f2229d909e78e90cc1bb9dfd16d3ea721a8f7a185c13774b5`
- allowed top-level directories: `81`
- allowed top-level files: `29`
- sanctioned source-like roots: `4`

## No `src` Rule

Generic code dumping grounds remain forbidden:

- top-level `src/`
- top-level `source/`
- top-level `Source/` or `Sources/`
- any unsanctioned nested `src` or `source` directory that is not policy-classified in Xi-5x2/Xi-8

Source-like roots that remain are allowed only through explicit Xi-5x2/Xi-8 policy.

## Canonical Domain Placement

- `engine`: Deterministic engine-kernel and runtime law surfaces.
- `game`: Game-layer rules, domain content, and gameplay-specific orchestration.
- `apps`: User-facing applications, shells, launchers, setup flows, and product entrypoints.
- `tools`: Governed tooling, validation, release, audit, and operator support surfaces.
- `lib`: Shared libraries and reusable support code for non-product surfaces.
- `compat`: Compatibility negotiation, shims, and controlled legacy transition bridges.
- `ui`: Presentation and user-interface surfaces kept separate from truth mutation.
- `platform`: Platform adapters and environment-specific integration points.
- `data`: Derived artifacts, baselines, registries, inventories, and frozen machine-readable surfaces.
- `docs`: Canonical doctrine, audits, blueprints, and human-readable policy surfaces.

## Frozen Top-Level Layout

| Primary Domain | Roots |
| --- | --- |
| `apps` | ``app`, `client`, `launcher`, `server`, `setup`` |
| `appshell` | ``appshell`` |
| `archive` | ``archive`` |
| `artifacts` | ``artifacts`` |
| `astro` | ``astro`` |
| `attic` | ``attic`` |
| `chem` | ``chem`` |
| `cmake` | ``cmake`` |
| `compat` | ``compat`` |
| `control` | ``control`` |
| `core` | ``core`` |
| `data` | ``data`` |
| `diag` | ``diag`` |
| `diegetics` | ``diegetics`` |
| `dist` | ``dist`` |
| `docs` | ``docs`` |
| `electric` | ``electric`` |
| `embodiment` | ``embodiment`` |
| `engine` | ``engine`, `worldgen`` |
| `epistemics` | ``epistemics`` |
| `field` | ``field`` |
| `fields` | ``fields`` |
| `fluid` | ``fluid`` |
| `game` | ``game`` |
| `geo` | ``geo`` |
| `governance` | ``.github`, `governance`` |
| `ide` | ``.vscode`, `ide`` |
| `infrastructure` | ``infrastructure`` |
| `inspection` | ``inspection`` |
| `interaction` | ``interaction`` |
| `interior` | ``interior`` |
| `labs` | ``labs`` |
| `legacy` | ``legacy`` |
| `lib` | ``lib`, `libs`` |
| `locks` | ``locks`` |
| `logic` | ``logic`` |
| `logistics` | ``logistics`` |
| `machines` | ``machines`` |
| `materials` | ``materials`` |
| `mechanics` | ``mechanics`` |
| `meta` | ``meta`` |
| `mobility` | ``mobility`` |
| `modding` | ``modding`` |
| `models` | ``models`` |
| `net` | ``net`` |
| `packs` | ``bundles`, `packs`` |
| `performance` | ``performance`` |
| `physics` | ``physics`` |
| `pollution` | ``pollution`` |
| `process` | ``process`` |
| `profiles` | ``profiles`` |
| `quarantine` | ``quarantine`` |
| `reality` | ``reality`` |
| `release` | ``release`` |
| `repo` | ``repo`` |
| `runtime` | ``runtime`` |
| `safety` | ``safety`` |
| `schemas` | ``schema`, `schemas`` |
| `security` | ``security`` |
| `signals` | ``signals`` |
| `specs` | ``specs`` |
| `system` | ``system`` |
| `templates` | ``templates`` |
| `tests` | ``tests`` |
| `thermal` | ``thermal`` |
| `tools` | ``scripts`, `tools`` |
| `ui` | ``ui`` |
| `universe` | ``universe`` |
| `updates` | ``updates`` |
| `validation` | ``validation`` |

Top-level files kept in the lock:

- `.gitattributes`, `.gitignore`, `AGENTS.md`, `CHANGELOG.md`, `CMakeLists.txt`, `CMakePresets.json`, `CODE_CHANGE_JUSTIFICATION.md`, `CONTRIBUTING.md`, `DOMINIUM.md`, `GOVERNANCE.md`, `LICENSE.md`, `MODDING.md`, `README.md`, `SECURITY.md`, `VERSION_CLIENT`, `VERSION_ENGINE`, `VERSION_GAME`, `VERSION_LAUNCHER`, `VERSION_SERVER`, `VERSION_SETUP`, `VERSION_SUITE`, `VERSION_TOOLS`, `__init__.py`, `meta_extensions_engine.py`, `numeric_discipline.py`, `sitecustomize.py`, `tool_ui_bind.cmd`, `tool_ui_doc_annotate.cmd`, `tool_ui_validate.cmd`

## Allowed Source-Like Exceptions

| Root | Policy Class | Rationale |
| --- | --- | --- |
| `attic/src_quarantine/legacy/source` | `VALID_LEGACY_ARCHIVE_SOURCE` | attic/src_quarantine/legacy/source is retained as explicit quarantine evidence and is fenced from active runtime and build ownership. |
| `attic/src_quarantine/src` | `VALID_LEGACY_ARCHIVE_SOURCE` | attic/src_quarantine/src is retained as explicit quarantine evidence and is fenced from active runtime and build ownership. |
| `legacy/source` | `VALID_LEGACY_ARCHIVE_SOURCE` | legacy test pocket is retained as archival reference and is not wired into active top-level build entrypoints |
| `packs/source` | `VALID_CONTENT_SOURCE` | source packs are upstream data inputs and are excluded from default dist output unless explicitly selected |

## Prohibited Patterns

- new unknown top-level directories without registry and lock updates
- new top-level `src` or `source` directories
- new nested source-like roots outside the sanctioned Xi-5x2/Xi-8 allowlist
- generic common dumping grounds introduced without architectural registration

Ignored generated surfaces such as `build/`, `dist/`, `out/`, `tmp/`, `.xstack_cache/`, and projection output trees are not part of this lock.
