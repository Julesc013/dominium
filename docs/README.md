Status: DERIVED
Last Reviewed: 2026-06-17
Supersedes: legacy `docs/README.md` patch-note orientation
Superseded By: none
Stability: provisional
Future Series: PUBLIC-DOCS
Replacement Target: long-lived documentation root derived from canon, status, roadmap, and public docs stack

# Dominium Documentation

This directory contains Dominium's public, canonical, derived, development, and
archival documentation. Use this page as the documentation root after reading
the top-level `README.md`.

This page is derived. If it conflicts with `docs/canon/constitution_v1.md`,
`docs/canon/glossary_v1.md`, `AGENTS.md`, active contracts, `.aide/queue/current.toml`,
or reviewed audits, the higher-authority artifact wins.

## Public Docs Stack

| Surface | Role |
|---|---|
| `README.md` | Public front door: project positioning, status, quick start, architecture sketch, and navigation. |
| `DOMINIUM.md` | Public product overview for Domino, Dominium, Workbench, product surfaces, and audience paths. |
| `docs/STATUS.md` | Current public truth boundary: implemented, blocked, validation, and evidence sources. |
| `docs/ARCHITECTURE.md` | Public architecture overview and system diagram. |
| `docs/ROADMAP.md` | Public sequencing guide and claim ledger for planned/blocked work. |
| `CONTRIBUTING.md` | Human contributor workflow. |
| `GOVERNANCE.md` | Public governance summary; `AGENTS.md` remains the canonical agent/human governance contract. |
| `MODDING.md` | Public pack and modding boundary. |
| `AGENTS.md` | Canonical operating contract for agents and humans doing repo-grounded work. |

## Reader Paths

| Reader goal | Start here | Then read |
|---|---|---|
| Understand the project in 60 seconds | `README.md` | `DOMINIUM.md` |
| Check what is real now | `docs/STATUS.md` | `.aide/queue/current.toml`, `docs/repo/FOUNDATION_LOCK.md` |
| Understand the system shape | `docs/ARCHITECTURE.md` | `docs/architecture/CANONICAL_SYSTEM_MAP.md`, `docs/architecture/CANON_INDEX.md` |
| See what may happen next | `docs/ROADMAP.md` | current queue and reviewed audits |
| Build and verify locally | `docs/development/guides/BUILDING.md` | `contracts/testing/test_tiers.contract.toml` |
| Contribute code/docs/data | `CONTRIBUTING.md` | `AGENTS.md`, relevant contracts |
| Work on packs or content | `MODDING.md` | `content/README.md`, `content/packs/README.md`, `contracts/package/packs/README.md` |
| Operate as an agent | `AGENTS.md` | `.aide/context/latest-task-packet.md` if present/relevant |

## Authority Order

For repo-grounded decisions, use this order:

1. `docs/canon/constitution_v1.md`
2. `docs/canon/glossary_v1.md`
3. `AGENTS.md`
4. Active contracts, registries, queue state, and reviewed audits
5. Canonical architecture documents under `docs/architecture/`
6. Public derived docs such as `README.md`, `DOMINIUM.md`, this file,
`docs/STATUS.md`, `docs/ARCHITECTURE.md`, and `docs/ROADMAP.md`
7. Archived or superseded documents, for provenance only

Prompts, chat summaries, generated echoes, and convenience summaries do not
outrank repository truth.

## Documentation Taxonomy

| Area | Meaning |
|---|---|
| `docs/canon/` | Highest-level constitutional and glossary authority. |
| `docs/architecture/` | Canonical and derived architecture, contracts, system maps, ownership notes, and detailed design law. |
| `docs/repo/` | Repository status, layout, audits, foundation lock, and repo-operational docs. |
| `docs/development/` | Build, language, platform, and developer workflow guidance. |
| `docs/release/` | Release, roadmap, matrix, and publication-related material. Public release remains blocked until explicitly opened. |
| `docs/content/` | Content and pack explanation where present. |
| `docs/modding/` | Modding guidance where present. Top-level `MODDING.md` is the public entrypoint. |
| `docs/reference/` | Reference docs and compatibility material where present. |
| `docs/planning/` | Planning and execution-state materials; use with authority-order caution. |
| `docs/archive/` | Historical, superseded, quarantined, or provenance-retained material. Not public truth unless promoted by a higher authority. |

## Current Public Status Rule

Public docs must preserve the distinction between:

```text
Implemented
In review
Experimental
Planned
Blocked
Not planned / not current trust model
```

Do not describe planned or blocked work as implemented. In particular, do not
claim release readiness, complete Workbench UI, gameplay, renderer/native GUI,
provider runtime, package runtime, runtime module loading, or arbitrary
executable mods while the current queue keeps those areas blocked.

## Core Mental Model

- The deterministic substrate owns authoritative execution mechanics.
- Dominium gives those mechanics game/product meaning.
- Contracts and registries define public law.
- Content and packs supply authored payload, not hidden runtime authority.
- Projection surfaces display or operate on command/result/refusal truth.
- Evidence, diagnostics, validators, audits, and tests constrain public claims.

## Maintenance Loop

When project state changes:

1. Update the governing artifact first: canon, contract, registry, queue, test,
or reviewed audit.
2. Update `docs/STATUS.md` if current truth changed.
3. Update `docs/ROADMAP.md` if sequencing or authorization changed.
4. Update `docs/ARCHITECTURE.md` only if the public architecture model changed.
5. Update `DOMINIUM.md` and `README.md` only if the public front-door story
changed materially.
6. Keep blocked areas visible until a higher-authority artifact explicitly opens
them.

## Archival Notes

Archived documents are retained for provenance and reconstruction. They should
not be used to override canon, glossary, `AGENTS.md`, active contracts, current
queue state, or reviewed audits.
