# Dominium — Directory Context (Authoritative)

This document is the authoritative directory/layout contract for this
repository. If another document disagrees on paths or module placement, this
file is the source of truth.

## Repository layout

```
dominium/
├── docs/                     – specifications and policy docs (authoritative)
├── engine/                   – Domino engine sources + headers
│   ├── include/              – public engine API (domino/*)
│   ├── modules/              – engine subsystem implementations
│   ├── render/               – render backends and glue
│   └── tests/                – engine tests (optional build)
├── game/                     – Dominium game sources + headers
│   ├── include/              – public game API (dominium/*)
│   ├── core/                 – shared game logic
│   ├── rules/                – authoritative rules
│   ├── economy/              – economy systems
│   ├── ai/                   – AI scaffolding
│   ├── content/              – game content sources
│   ├── mods/                 – mod-facing integration
│   ├── ui/                   – UI semantics (non-rendering)
│   └── tests/                – game tests and fixtures
├── client/                   – client executable entrypoint
├── server/                   – server executable entrypoint
├── launcher/                 – launcher core + frontends
├── setup/                    – setup core + frontends
├── tools/                    – tool host + validators/editors
├── libs/                     – interface libraries and shared contracts
├── schema/                   – data schemas and validation docs
├── sdk/                      – SDK headers, docs, and samples
├── scripts/                  – build helpers and packaging automation
├── cmake/                    – CMake modules used by the root build
├── legacy/                   – archived sources excluded from current builds
├── build/                    – out-of-source build directory (ephemeral)
├── dist/                     – build outputs (ephemeral)
└── .github/                  – workflow/CI configuration
```

## Domino engine subdirectories (module boundaries)

`engine/modules/` contains both deterministic core subsystems and non-authoritative
runtime/front-end subsystems:

- Deterministic core subsystems (must obey `docs/SPEC_DETERMINISM.md`):
  `core/`, `sim/`, `world/`, `trans/`, `struct/`, `decor/`, `agent/`, plus the
  deterministic parts of `env/`, `res/`, `build/`, `job/`, `net/`, `replay/`,
  `vehicle/`, and other stateful domains.
- Platform/system layer: `system/` and `sys/` – may call OS APIs; MUST NOT be used as
  inputs to deterministic simulation decisions.
- Rendering: `engine/render/` and render-facing headers – derived outputs only.
- UI/view: `ui/` and `view/` – derived presentation and event routing; never
  authoritative.

Domino public headers live under `engine/include/domino/`. Dominium product code
MUST NOT include private headers from `engine/modules/**`; use
`engine/include/domino/**` only.

## DOMINIUM_HOME / DOMINIUM_RUN_ROOT

Filesystem root contracts are defined in `docs/SPEC_FS_CONTRACT.md` and
`engine/include/domino/pkg/repo.h`. This repository does not ship a `repo/`
runtime tree; runtime layouts live outside the source tree.
