# Dominium — Directory Context and Contract (Launcher/Setup Refresh)

This file is the binding map for the repository. All work in this change-set must follow it. Anything that conflicts with these rules is considered a bug even if it compiles.

---

## Top-level layout
- `/docs` — specs, architecture notes, API docs, formats, context packs.
- `/include` — installable headers. `include/dominium/*` is public (dom_core.h, dom_plat.h, dom_rend.h, dom_launcher_api.h, dom_game_mod_api.h, dom_package_manifest.h, dom_version.h). `include/dom_priv/*` is internal-only (shared utilities, build version, launcher/setup private headers).
- `/source` — main code tree (core/platform/renderer/game/launcher/setup/tools) plus `_legacy` quarantine. **Note:** modding/data/script/native/sandbox/package loaders are now under `source/core` instead of a separate `/modding` subtree.
- `/tools` — built tool entrypoints (dom_inspect, dom_validate_content, future dom_assetc/dom_pack/etc.).
- `/data` — first-party data packs (base/DLC/packs/templates/schema). The same loader code is shared with `/mods`.
- `/mods` — third-party/local mods (manifests + data/scripts/assets/tests) consumed by the unified loader.
- `/external` and `/third_party` — vendored deps with pins/licenses only.
- `/tests` — deterministic/unit/integration/perf tests; small launch/setup stubs allowed.
- `/packaging` — installer/image definitions and branding assets.
- `/scripts` — repo automation/maintenance; no runtime logic.
- `/cmake` — toolchains/modules (currently stubs).
- `/build` — build/preset outputs (never committed).

No new top-level directories may be introduced without updating this file first.

---

## Directory rules (high level)

### `/docs`
- Authoritative specs live in `docs/spec` and `docs/API`/`docs/FORMATS`.
- Context packs and non-binding notes live in `docs/context` and `docs/dev`.
- No binaries or generated assets.

### `/include`
- `dominium/*` exposes public ABI/manifest headers only; keep it minimal and C89/C++98 friendly.
- `dom_priv/*` holds internal headers shared across products (dom_shared, dom_launcher, dom_setup, dom_build_version, dom_keys).
- Public headers may temporarily forward to internal headers while APIs are stabilised; mark TODOs where this happens.

### `/source/core`
- Deterministic C89 engine code plus shared libs and the merged modding/packaging stack.
- Subdirs: `base` (dom_core low-level + RNG/types), `math` (fixed-point), `serialize` (save formats), `sim` (ECS/world/registries + dom_sim experiments), `audio` (stub), `ui` (stub), `base/shared` (C++98 dom_shared utilities for launcher/setup/tools), and modding/data loaders under `data`, `package`, `script`, `native`, `sandbox`, `vfs`.
- No platform/renderer headers in core; no floats in deterministic paths; keep save formats stable. The same loaders serve `/data` and `/mods`.

### `/source/platform`
- Platform backends (`win32`, `sdl1`, `sdl2`, `x11`, `wayland`, `cocoa`, `shared/posix_headless`). Currently scaffolded; dom_plat.h is the contract. Wire OS headers only inside this layer.

### `/source/renderer`
- Renderer API/backends behind dom_rend.h. `core` + `soft` (software/null) build now; hardware backends (dx9/dx11/gl/vk) staged with TODOs and must route through platform abstractions.

### `/source/launcher`
- C++98 launcher logic under `core/`; frontends under `cli/`, `tui/`, `gui/`. Uses dom_shared + dom_launcher headers only; never links to dom_engine. Plugin ABI exposed via dom_launcher_api.h.

### `/source/setup`
- `core/` install/repair/uninstall/info logic; `cli/` entrypoint. Uses dom_shared + dom_setup headers; OS-specific hooks live under `os/`. `sdk/` holds setup-facing extension surface if present.

### `/source/game`
- Game shells built on dom_engine/dom_core via C ABI. `cli/` (dom_cli + server), `gui/` (dom_main dispatcher), `core/` (client glue + input), `sdk/` (game mod-facing surface), plus `states/`, `ui/`, `tui/` as they come online. Deterministic state stays float-free; renderer/platform access must be through dom_rend/dom_plat once wired.

### `/source/tools`
- Internal tool libraries (assetc/packer/diagnostics/test harness) that feed the top-level `/tools` entrypoints. Keep deterministic where they touch save/content formats.

### `/source/_legacy`
- Quarantine for obsolete/dead code that must not block refactors. Every file here needs a `// LEGACY: candidate for removal/refactor` banner and no new dependencies.

### `/tools`
- Built tool entrypoints only; they reuse libs from `src/*` instead of re-implementing formats.

### `/packaging`
- Installer/image definitions and wrapping scripts. Binaries referenced here must match targets from `/src/products/*`.

### `/scripts`
- Automation/maintenance; must be explicit about any tracked-file changes.

### `/tests`
- Tests only (unit/integration/replay/perf); no OS randomness or network without explicit fixtures. Keep deterministic seeds and avoid floats in core checks.

General rule: engine determinism and layering are enforced across all directories. Products must route through manifests and public APIs instead of reaching into simulation internals directly. Keep platform/renderer separations strict and float-free in core save paths.
