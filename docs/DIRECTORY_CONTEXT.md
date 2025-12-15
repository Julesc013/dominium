# Dominium — Directory Context (Authoritative)

This document is the authoritative directory/layout contract for this
repository. If another document disagrees on paths or module placement, this
file is the source of truth.

## Repository layout

```
dominium/
├── docs/                     – specifications and policy docs (authoritative)
├── include/                  – public headers
│   ├── domino/               – Domino engine public API (and `domino/_internal/`)
│   └── dominium/             – Dominium product-facing headers
├── source/                   – all source code
│   ├── domino/               – Domino engine implementation
│   ├── dominium/             – Dominium products (common, game, launcher, setup, tools)
│   └── tests/                – buildable unit-style tests (C/C++)
├── tests/                    – integration-style tests and fixtures
├── data/                     – in-tree content source (authoring/packs/mods/versions/test)
├── repo/                     – runtime repository layout used by `DOMINIUM_HOME` tooling
├── scripts/                  – build helpers and packaging automation
├── cmake/                    – CMake modules used by the root build
├── external/                 – vendored third-party sources
├── build/                    – out-of-source build directory (ephemeral)
└── .github/                  – workflow/CI configuration
```

## Domino engine subdirectories (module boundaries)

`source/domino/` contains both deterministic core subsystems and non-authoritative
runtime/front-end subsystems:

- Deterministic core subsystems (must obey `docs/SPEC_DETERMINISM.md`):
  `core/`, `sim/`, `world/`, `trans/`, `struct/`, `decor/`, `agent/`, plus the
  deterministic parts of `env/`, `res/`, `build/`, `job/`, `net/`, `replay/`,
  `vehicle/` and other stateful domains. Legacy AI/agent scaffolding also exists
  under `ai/` (see `docs/SPEC_AGENT.md`).
- Platform/system layer: `system/` (dsys) – may call OS APIs; MUST NOT be used as
  an input to deterministic simulation decisions.
- Rendering: `render/` and `gfx`/canvas APIs – derived outputs only; never
  authoritative.
- UI/view: `ui/` and `view/` – derived presentation and event routing; never
  authoritative.

Domino public headers live under `include/domino/`. Dominium product code MUST
NOT include private headers from `source/domino/**`; use `include/domino/**`
only.

## DOMINIUM_HOME (runtime/tooling root)

Dominium tools and products treat `DOMINIUM_HOME` as a root for a runtime repo
layout (see `source/dominium/common/dom_paths.*`):

- `repo/products/` – product manifests (and/or build outputs staged for launch)
- `repo/packs/` – pack blobs (`pack.tlv`/`pack.bin`) by id and version
- `repo/mods/` – mod blobs (`mod.tlv`/`mod.bin`) by id and version
- `instances/` – per-instance roots (metadata, saves, logs)
- `temp/` – scratch space for setup/tools
