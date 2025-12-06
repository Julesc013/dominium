# Dominium — Directory Context and Contract (Launcher/Setup Refresh)

This file is the binding map for the repository. All launcher/setup work in this change-set must follow it. Anything that conflicts with these rules is considered a bug even if it compiles.

---

## Top-level layout
- `/docs` — specs, architecture notes, API docs, formats, context packs.
- `/engine` — deterministic C89 core; fixed-point only; no platform/renderer/audio headers outside `engine/platform|render|audio`.
- `/runtime` — C++98 frontends and shells that wrap the engine via the C ABI (dom_cli/dom_sdl/etc.).
- `/game` — Dominium-specific logic and runtimes (C/C++98) built on the engine C ABI (client/server shells, game glue, thin launch entrypoints).
- `/launcher` — C++98 multi-mode launcher (CLI/TUI/GUI), install discovery, process supervision, profiles/mods/tools wiring; never links the engine.
- `/setup` — `dom_setup` C++98 tool for install/repair/uninstall/list/info and install manifests.
- `/shared` — cross-cutting utilities (paths, JSON, logging, UUID, manifest helpers) used by launcher/setup/tools.
- `/tools` — standalone utilities (C/C++/scripts) that reuse engine IO or runtime CLIs; offline editors, validators, SDK helpers.
- `/data` — first-party data packs (base/DLC/packs/templates/schema).
- `/mods` — third-party/local mods (manifests + data/scripts/assets/tests).
- `/tests` — deterministic/unit/integration/perf tests; may include small launch/setup stubs.
- `/external` and `/third_party` — vendored deps with pins/licenses only.
- `/build` — CMake glue, toolchains, presets, helper scripts.
- `/packaging` — installer/image definitions and branding assets.
- `/scripts` — repo automation/maintenance; no runtime logic.
- `/ports` — experimental/retro targets; build isolation required.

No new top-level directories may be introduced without updating this file first.

---

## Directory rules (high level)

### `/docs`
- Authoritative specs live in `docs/spec` and `docs/API`/`docs/FORMATS`.
- Context packs and non-binding notes live in `docs/context` and `docs/dev`.
- No binaries or generated assets.

### `/engine`
- Deterministic C89 core; fixed-point only.
- Platform/render/audio headers only under their dedicated subdirs.
- No Dominium-specific content, mods, or OS calls in core/sim.

### `/runtime`
- C++98 frontends wrapping the engine via the C ABI (CLI/headless, SDL/GUI shells, server stubs).
- Must remain functional without the launcher; honour `--display`, `--version`, and `--capabilities` flags.
- May use floats internally for rendering/UI but never feed floating-point values back into deterministic engine state.

### `/game`
- Dominium gameplay/frontends built on engine C ABI.
- Client/server shells live here (C/C++98), plus minimal launch entrypoints.
- No platform headers outside engine platform wrappers; no determinism violations.

### `/launcher`
- Core launcher code (C++98): install discovery, manifest reading, profiles, mod sets, server/browser/social/tool hooks, instance supervision, and UI frontends (CLI/TUI/GUI stubs). Core state/DB/discovery scaffolding lives under `launcher/src/core`.
- Uses runtime CLIs and manifests only; does not link against `/engine`.
- Plugin-ready API for tabs/commands; stores launcher DB under user/portable data roots.

### `/setup`
- `dom_setup` tool, install manifest handling, OS path helpers, and CLI for install/repair/uninstall/list/info.
- Writes `dominium_install.json` into every install root; registers installs conservatively (registry/index files where allowed).
- Plugin-ready architecture for install profiles and hooks (stubs allowed until plugins exist).

### `/shared`
- Common infrastructure for non-engine code: path helpers, JSON reader/writer, logging, UUIDs, process helpers, manifest helpers.
- Linkable from launcher/setup/tools; no engine dependencies.

### `/tools`
- Offline utilities, editors, validators, SDK/pipeline helpers.
- Must reuse engine IO or runtime CLIs instead of reimplementing formats.

### `/data`
- First-party packs with explicit manifests; no code, no third-party mods.

### `/mods`
- Third-party/local mods with `mod.json` and optional data/scripts/assets/tests; sandbox/determinism rules apply.

### `/tests`
- Tests only (unit/integration/replay/perf); no OS randomness or network without explicit fixtures.
- May build small launch/setup stubs to validate manifests and discovery.

### `/build`
- CMake modules/toolchains/presets and helper scripts; no authoritative specs or network fetches.

### `/packaging`
- Installer/image definitions and branding; no build outputs or runtime code.

### `/scripts`
- Automation/maintenance; must be explicit about any tracked-file changes.

### `/ports`
- Alternative/retro targets; must not change deterministic core.

General rule: engine determinism and layering are enforced across all directories. Any new launcher/setup/runtime work must route through manifests and CLIs rather than reading simulation internals directly.
