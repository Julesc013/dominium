# Dominium — Directory Context

Canonical layout (Domino = engine, Dominium = product family).

```
dominium/
├── docs/                     – specs, architecture notes, build docs.
├── include/                  – public headers (`domino/`, `dominium/`, `_internal/` for dom_shared and build metadata).
├── source/                   – all code.
│   ├── domino/               – reusable engine stack.
│   │   ├── system/           – domino_sys platform layer (core dispatch, terminal/UI stubs, platform backends).
│   │   ├── render/           – domino_gfx API plus software backend/targets and staged DX/GL/VK hooks.
│   │   ├── sim/              – ECS/world/replay scaffolding and serialization helpers.
│   │   └── mod/              – package/mod/script hosts (placeholders).
│   └── dominium/             – Dominium-specific logic.
│       ├── rules/            – rules/gameplay data stubs.
│       └── products/         – shipping products.
│           ├── launcher/     – launcher runtime, services, and shell frontends.
│           │   ├── core/     – launcher runtime, context, registry, view registry, process control.
│           │   ├── model/    – view models for launcher (instances, mods, packs, etc.).
│           │   ├── services/ – launcher services (instances/mods/packs/servers/accounts/tools).
│           │   │   └── instances/ – instances service (instance management and views).
│           │   ├── ipc/      – IPC stubs for future supervision.
│           │   ├── cli/      – CLI front-end for launcher.
│           │   ├── tui/      – TUI front-end (future).
│           │   └── gui/      – GUI front-end (future).
│           ├── setup/        – installer/repair/uninstall core + os hooks with cli/tui/gui.
│           │   ├── core/     – setup execution plans (install/repair/uninstall).
│           │   ├── model/    – discovery of installed products/manifests.
│           │   ├── cli/      – command-line installer/repair entrypoints.
│           │   └── gui/      – GUI installer stub.
│           └── game/         – game shells (core/client/app mode, states/ui, cli/tui/gui).
│               ├── core/     – game entrypoints and version helpers.
│               ├── states/   – gameplay state machine stubs.
│               ├── ui/       – shared UI glue.
│               ├── cli/      – command-line runner.
│               ├── tui/      – text UI shell (stub).
│               └── gui/      – rendered UI/graphics frontends.
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

## Notable engine subdirectories
- `source/domino/system/core` – platform-agnostic domino_sys core, terminal, and native UI stubs.
- `source/domino/system/plat/*` – per-platform sys backends (win32/posix/null in this pass).
- `source/domino/render/api` – public-facing domino_gfx core, backend selection.
- `source/domino/render/soft` – software renderer core plus present targets (`null`, `win32` now; others TODO).
