Status: CANONICAL
Last Reviewed: 2026-02-14
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Repository Intent (CLEAN1)

Status: binding.
Scope: authoritative map of repository purpose, stability, and allowed change classes.

This document centralizes repository intent and links to the canonical contract index.
Normative contracts live under `docs/architecture/` only. See `docs/architecture/CONTRACTS_INDEX.md`.

## Top-level directory intent

| Directory | Purpose | Allowed changes | Stability |
| --- | --- | --- | --- |
| `.github/` | CI workflows and automation | CI-only adjustments, no runtime behavior | Evolving |
| `.vs/`, `.vscode/`, `ide/` | Editor and IDE configuration | Tooling comfort only | Evolving |
| `app/` | App shell and presentation integration | Presentation-only changes via UX prompts | Evolving |
| `build/`, `out/` | Local build outputs | No tracked source changes | Quarantined |
| `ci/` | CI scripts and checks | CI-only adjustments | Evolving |
| `client/` | Client presentation layer | Presentation-only changes, no simulation logic | Evolving |
| `cmake/` | Build system modules | Build configuration only | Evolving |
| `data/` | Data packs and fixtures | Data-only changes, no code | Frozen (pack formats), Evolving (content) |
| `bundles/` | Governed bundle fixtures and serialized bundle artifacts | Bundle/schema-preserving changes only | Evolving |
| `dist/` | Distribution artifacts and layout | Packaging only | Evolving |
| `repo/` | Pack output repository (generated packs) | Generated pack outputs only | Quarantined |
| `updates/` | Update feeds and channel metadata | Packaging metadata only | Evolving |
| `docs/` | Documentation | See doc taxonomy below | Frozen/Evolving per taxonomy |
| `engine/` | Engine runtime | Code changes only when explicitly allowed by prompt | Frozen (public contracts), Evolving (internals) |
| `game/` | Game runtime | Code changes only when explicitly allowed by prompt | Frozen (public contracts), Evolving (internals) |
| `labs/` | Experimental or research prototypes | Quarantined, no mainline build usage | Quarantined |
| `launcher/` | Launcher & setup integration | Orchestration-only changes | Evolving |
| `legacy/` | Archived legacy artifacts | Archive only, no new features | Archived |
| `libs/` | Shared libraries and contracts | Contract-preserving changes only | Frozen (contracts), Evolving (impl) |
| `locks/` | Canonical lock artifacts used by MVP/runtime packaging | Packaging/verification changes only | Evolving |
| `packs/` | Canonical pack manifests and data-only pack contributions | Data-only pack changes; no executable code | Evolving |
| `profiles/` | Canonical profile and bundle selections | Profile/packaging changes only | Evolving |
| `quarantine/` | Isolated local artifacts held outside mainline release intent | Quarantine only, no runtime coupling | Quarantined |
| `schema/` | Schema contracts | Contracted schema edits only | Frozen/Evolving per `SCHEMA_STABILITY.md` |
| `schemas/` | Generated or composed schema artifacts | Generated artifacts and schema bundle exports only | Quarantined |
| `src/` | Governed Python runtime, validation, release, and tooling implementation | Contract-preserving code changes only | Frozen (public contracts), Evolving (internals) |
| `scripts/` | Developer scripts | Non-runtime tooling only | Evolving |
| `sdk/` | SDK and integration surfaces | Contract-preserving changes only | Evolving |
| `server/` | Server runtime | Code changes only when explicitly allowed by prompt | Frozen (public contracts), Evolving (internals) |
| `shared_ui_win32/` | Win32 UI renderer stubs for app shells | Presentation-only changes, no simulation logic | Evolving |
| `setup/` | Installer/setup workflows | Orchestration-only changes | Evolving |
| `templates/` | Canonical authored template inputs and generated template fixtures | Template/schema-preserving changes only | Evolving |
| `tests/` | TESTX suites and fixtures | Test-only changes, no runtime behavior | Evolving |
| `tools/` | Read-only tools and inspectors | Tool-only changes, no simulation authority | Evolving |
| `tmp/` | Local scratch space | Quarantined, no mainline usage | Quarantined |
| `run_meta/` | Generated run metadata and deterministic execution receipts | Generated artifacts only | Quarantined |
| `saves/` | Local save artifacts and save-fixture outputs | Fixture/save pipeline changes only | Quarantined |
| `worldgen/` | Worldgen source assets, intermediate fixtures, and governed generation inputs | Data/tooling changes only, no gameplay semantics bypass | Evolving |

## Documentation taxonomy (normative location)

Normative contracts live in `docs/architecture/` only. Other documentation categories:

- `docs/roadmap/` is goals and tests only.
- `docs/content/` is data explanation only.
- `docs/dev/` and `docs/modding/` are how-to only.

Non-architecture docs must link to their canonical contract counterparts when relevant.

## Quarantine and archive rule

Directories marked Quarantined or Archived are excluded from mainline build intent.
They remain for historical reference or future revival only, with local README files
documenting purpose and revival criteria.
