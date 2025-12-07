# Dominium — Directory Context

Canonical layout (Domino = engine, Dominium = product family).

```
dominium/
├── docs/                     – specs, architecture notes, build docs.
├── include/                  – public headers (`domino/`, `dominium/`, `_internal/` for dom_shared and build metadata).
├── source/                   – all code.
│   ├── domino/               – reusable engine stack.
│   │   ├── system/           – core runtime (math, logging, shared utils) and platform stubs/backends.
│   │   ├── render/           – renderer API plus software/null targets and staged DX/GL/VK hooks.
│   │   ├── sim/              – ECS/world/replay scaffolding and serialization helpers.
│   │   └── mod/              – package/mod/script hosts (placeholders).
│   └── dominium/             – Dominium-specific logic.
│       ├── rules/            – rules/gameplay data stubs.
│       └── product/          – shipping products.
│           ├── launcher/     – launcher core/model/ipc plus cli/tui/gui frontends.
│           ├── setup/        – installer/repair/uninstall core + os hooks with cli/tui/gui.
│           └── game/         – game shells (core/client/app mode, states/ui, cli/tui/gui).
├── data/                     – content tree.
│   ├── authoring/            – raw source assets (graphics/sounds/music/misc).
│   ├── packs/                – packaged assets (`graphics/`, `sounds/`, `music/` with base/space/war variants).
│   ├── mods/                 – first-party/example mods (base/space/war/examples).
│   └── test/                 – deterministic fixture data.
├── tools/                    – top-level tool entrypoints (stubbed).
├── tests/                    – unit/integration harnesses.
├── scripts/                  – automation and build/CI helpers.
├── cmake/                    – CMake presets/toolchains/modules.
├── external/                 – vendored dependencies.
└── .github/                  – workflow/CI configuration.
```
