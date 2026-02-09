# Dominium / Domino

## 1. Project Overview
Dominium is a multi-product platform for deterministic simulation and long-lived
runtime operation. Domino (engine) provides the deterministic core; Dominium (game)
defines the authoritative rules and data-driven simulation on top of it. The repo
also includes the launcher, setup, server, client, and tools needed to operate
the platform without depending on external packs or assets.

This repository is not a monolithic game, not asset-dependent, and not bound to
any single renderer or operating system. It is designed to survive OS churn,
toolchain shifts, and long-term modability while keeping authoritative outcomes
reproducible across builds.

## 2. Repository Organization
Responsibilities, non-goals, and UI expectations by area:
- `engine/` (Domino): deterministic core runtime, simulation substrate, platform
  and renderer interfaces. Must not depend on platform-specific UI, app layers,
  or game rules. UI expectation: none.
- `game/` (Dominium): authoritative game rules and data-driven simulation logic.
  Must not depend on platform/runtime/UI layers. UI expectation: none.
- `client/`: user-facing runtime shell that links engine + game. Must not embed
  assets or game logic; must support CLI/TUI/GUI. Client GUI is renderer-driven.
- `server/`: headless authoritative runtime shell. Must not link windowing, GUI,
  or GPU renderers. UI expectation: CLI/TUI/GUI modes exist; GUI may be stubbed.
- `launcher/`: control-plane orchestration, capability probes, and launch
  handshakes. Must not contain engine/game logic. UI expectation: CLI/TUI/GUI
  modes exist; GUI may be stubbed or native.
- `setup/`: install/bootstrap responsibilities and layout preparation. Must not
  contain engine/game logic. UI expectation: CLI/TUI/GUI modes exist; GUI may be
  stubbed or native.
- `tools/`: inspection, validation, replay/viewer stubs, and artifact utilities.
  Must remain CLI-first; optional TUI/GUI shells allowed. No gameplay authority.
- `app/`: shared app-layer runtime utilities (loop/timing, CLI, build-info,
  compatibility checks). Must not become engine/game dependency.
- `engine/modules/system/`: platform runtime (dsys) implementation. Must not
  leak OS details into engine/game or app logic.
- `engine/render/`: renderer backends and registry (dgfx). Must not include
  simulation/gameplay headers or logic.
- `docs/`: canonical contracts, policies, and TestX/RepoX guidance.
- `tests/`: TestX and enforcement tests (CLI-only; no GUI dependencies).

Abstracted tree (non-exhaustive):
```
/app
/client
/engine
  /include
  /modules/system        (platform runtime)
  /render                (renderer backends)
/game
/launcher
/setup
/server
/tools
/docs
/tests
/libs
/schema
```

## 3. Product Boundaries & Responsibilities (Canon)
Hard boundaries enforced by policy and tests:
- Engine/game vs apps: engine + game remain platform- and renderer-agnostic;
  apps must not include engine private headers.
- Renderer backends vs core logic: renderers are plugins; no renderer-specific
  logic or assets in engine/game.
- Platform runtime vs apps: OS integration is isolated behind dsys; no callbacks
  from platform threads directly into engine/game logic.
- Launcher/setup vs runtime apps: control-plane tools must not become runtime
  shells or change simulation behavior.

Forbidden couplings (non-exhaustive):
- Engine or game including app/platform/render headers.
- Server linking windowing or GPU backends.
- Render backends including simulation/gameplay headers.
- Apps embedding assets or requiring packs to boot.

## 4. Execution Modes
All products support the unified UI mode model:
- CLI (`--ui=none`): primary, mandatory, testable; deterministic paths live here.
- TUI (`--ui=tui`): optional runtime layer; never a test dependency.
- GUI (`--ui=gui`): optional runtime layer; never required.

Client GUI is renderer-driven (no native widgets required). Server/launcher/
setup/tools may use native OS UI later, but GUI is always optional and must not
block CLI/TUI. Tests remain CLI-only.

## 5. Renderer & Platform Model
Renderers are logical plugins registered in a backend registry. Selection occurs
at runtime with explicit failure on unavailable backends (no silent fallback).
Auto selection is permitted only when explicitly chosen and must log the choice.

Baseline guarantees:
- Null renderer supports headless/CLI-only operation.
- Software renderer provides a CPU-backed baseline.
- Shader caches are disposable; no renderer-specific assets are required.

Platform runtime (dsys) provides windowing, input, time, and OS services behind
stable interfaces and extensions. Headless operation is first-class across OSes.

Artifact renderer token:
- `renderer=multi` means multiple backends are compiled into one binary.

See `docs/render/README.md` and `docs/platform/README.md` for the full contract.

## 6. TESTX (Non-Negotiable)
TestX is the binding test contract that enforces CLI behavior, determinism,
and portability rules. It exists to prevent interface rot and silent behavior
changes across platforms and toolchains.

Key invariants:
- Tests are CLI-only (no GUI/TUI dependencies).
- No skipped tests.
- Explicit renderer selection fails loudly if unavailable.
- Deterministic paths do not depend on wall-clock.
- ABI/portability checks are enforced.

Run locally:
```
ctest --output-on-failure
```
Or use the gated build-number workflow:
```
cmake --build <build-dir> --target testx_all
```
See `docs/app/TESTX_INVENTORY.md` and `docs/app/TESTX_COMPLIANCE.md`.

## 7. REPOX (Structure & Enforcement)
RepoX defines repository layout, naming conventions, build discipline, and
integration hooks so new products and backends can be added without refactors.

Integration is modular:
- Products: register `dom_<product>` targets via `dom_register_product`.
- Renderers: register `dom_render_backend_<name>` targets.
- Platform backends: register `dom_platform_backend_<name>`.
- Tests: register via `dom_add_testx` with required labels.

Canonical hooks live in `cmake/DomIntegration.cmake` and are documented in
`docs/repox/APRX_INTEGRATION_HOOKS.md`.

## 8. Versioning & Build Identity
Versioning is fixed by canon:
- Global build number (gated by TestX).
- Per-product semver (client/server/launcher/setup/tools).
- Runtime build-info output is mandatory.
- Protocol/API/ABI mismatches fail loudly with explicit diagnostics.

Artifact naming (canonical):
```
<product>-<semver>+build.<n>-<os>-<arch>-<renderer>-<config>
```
Example (values vary):
```
client-0.0.0+build.1234-winnt-x64-multi-Release
```

Example build-info output (values vary):
```
product=client
product_version=0.0.0
sku=modern_desktop
engine_version=0.0.0
game_version=0.0.0
build_number=1234
build_id=b1234-abcdef123456
git_hash=abcdef1234567890
toolchain_id=c=MSVC-19.40;cxx=MSVC-19.40;toolset=144
toolchain_family=msvc
toolchain_version=19.40
toolchain_stdlib=msvc-stl
toolchain_runtime=static:msvc
toolchain_link=static
toolchain_target=winnt-x64
toolchain_os=winnt
toolchain_arch=x64
toolchain_os_floor=winnt:win10_1507
toolchain_config=Release
protocol_law_targets=LAW_TARGETS@1.0.0
protocol_control_caps=CONTROL_CAPS@1.0.0
protocol_authority_tokens=AUTHORITY_TOKEN@1.0.0
abi_dom_build_info=1
abi_dom_caps=1
api_dsys=1
platform_ext_window_ex_api=1
platform_ext_error_api=1
platform_ext_cliptext_api=1
platform_ext_cursor_api=1
platform_ext_dragdrop_api=1
platform_ext_gamepad_api=1
platform_ext_power_api=1
platform_ext_text_input_api=1
platform_ext_window_mode_api=1
platform_ext_dpi_api=1
api_dgfx=1
```
See `docs/build/ARTIFACT_IDENTITY_AND_METADATA.md` and `docs/app/CLI_CONTRACTS.md`.

## 9. Building the Project
Use CMake presets (canonical list in `CMakePresets.json` and
`docs/ci/BUILD_MATRIX.md`). Multiple toolchains are supported; no single vendor
is mandated.

Minimal configure/build:
```
cmake --preset <preset>
cmake --build --preset <preset>
```

SKU and platform selection are configured via CMake cache options:
- `DOM_BUILD_SKU` (modern_desktop/headless_server/devtools/legacy_desktop)
- `DOM_PLATFORM` (sdl2/win32/posix_x11/posix_headless/etc)
- `DOM_BACKEND_*` (soft/null/dx9/gl2/vk1/metal, as supported)

Start with CLI-only paths when validating changes. See `docs/guides/BUILDING.md`.

## 10. Running the Products (Zero Packs)
All examples are CLI-first and do not require packs:
```
client --smoke
client --ui=tui
client --ui=gui --renderer=soft
server --smoke
launcher --smoke
setup --smoke
tools --smoke
```
GUI mode for non-client products may report "not implemented" without affecting
CLI/TUI correctness. See `docs/app/CLI_CONTRACTS.md`.

## 11. Contributing Rules (Critical)
You may:
- Extend app-layer runtime utilities.
- Add new products/backends using RepoX hooks.
- Add CLI-only tests under existing TestX structure.

You must not:
- Refactor engine/game behavior or authority logic.
- Introduce GUI/TUI dependencies in tests.
- Add silent fallback or hidden platform hacks.
- Break build-number gating or versioning rules.

How to add:
- New product: add a top-level product directory, define `dominium_<product>`
  target, add `dom_<product>` alias, call
  `dom_register_product`, and register CLI tests with `dom_register_product_cli_tests`.
- Renderer backend: add `dom_render_backend_<name>` marker and register with
  `dom_register_renderer_backend`; add TestX coverage for explicit failure and
  capability reporting.
- Platform backend: implement under `engine/modules/system/` and register
  `dom_platform_backend_<name>`.
- Tests: use `dom_add_testx` and required labels; keep CLI-only.

See `docs/repox/APRX_INTEGRATION_HOOKS.md` and `docs/ci/CI_ENFORCEMENT_MATRIX.md`.

## 12. Roadmap Context (Non-Binding)
APR0–APR5 established the application/runtime contracts, renderer and platform
interfaces, UI mode layering, observability pipelines, build metadata, and CI
survivability. APRX integrates these with TestX/RepoX enforcement. Language
transition planning (C89/C++98 to C17/C++17) is documented in `docs/architecture/`.
Roadmap context does not weaken canon.

## 13. What This Repo Deliberately Does Not Do
- No embedded assets; zero-pack boot is required.
- No mandatory GUI; CLI must always work.
- No engine UI or platform UI in engine/game.
- No silent compatibility hacks.
- No monolithic installers or single-vendor lock-in.

## 14. Documentation Index
- App runtime and CLI contracts: `docs/app/README.md`
- Platform runtime and lifecycle: `docs/platform/README.md`
- Renderer interface and backends: `docs/render/README.md`
- Build, toolchain, and SKU model: `docs/build/TOOLCHAIN_MODEL.md`,
  `docs/build/SKU_MODEL.md`, `docs/build/OS_FLOOR_POLICY.md`
- TestX compliance: `docs/app/TESTX_INVENTORY.md`,
  `docs/app/TESTX_COMPLIANCE.md`, `docs/governance/TESTX_PROOF_MODEL.md`
- RepoX integration: `docs/governance/REPOX_RULESETS.md`,
  `docs/repox/APRX_INTEGRATION_HOOKS.md`
