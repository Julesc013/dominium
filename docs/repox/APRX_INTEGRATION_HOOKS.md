# APRX Integration Hooks (RepoX/TestX)

This document defines the canonical integration conventions for new products,
platform backends, and renderer backends. It is intended to keep additions
modular and TestX/RepoX aligned.

Helper functions live in `cmake/DomIntegration.cmake`.

## CMake integration conventions

### Products (client/server/launcher/setup/tools)
- Directory layout: top-level product directories (e.g., `client/`, `server/`).
- Target naming (authoritative build targets):
  - Executables: `dominium_<product>` (example: `dominium_client`).
  - Canonical alias: `dom_<product>` (example: `dom_client`).
- Registration hook:
  - Call `dom_register_product(<name> <target>)` in the product CMakeLists.

### Renderer backends
- Backend code lives under `engine/render/<backend>/`.
- Canonical target name: `dom_render_backend_<name>` (INTERFACE marker target).
- Registration hook:
  - Call `dom_register_renderer_backend(<name> AVAILABILITY <available|unavailable>)`.
- Backend registration function naming:
  - Backends should expose a registration function `d_gfx_<name>_register_backend()`
    that returns the backend vtable.

### Platform backends
- Platform runtime code lives under `engine/modules/system/`.
- Build selection is via `DOM_PLATFORM` (single active backend per build).
- Canonical target name: `dom_platform_backend_<name>` (INTERFACE marker target).
- Registration hook:
  - Call `dom_register_platform_backend(<name>)`.

## Test registration conventions (ctest)

- Use `dom_add_testx(NAME ... COMMAND ... LABELS ...)` for TestX-aligned tests.
- Required labels (use existing label names):
  - `testx`, `smoke`, `portability`, `buildmeta`.
- Each product must register version/build-info/smoke coverage:
  - Use `dom_register_product_cli_tests(<product> <version_test> <buildinfo_test> <smoke_test>)`.
- Each renderer backend must register:
  - explicit selection failure test when unavailable
  - capability/availability report test
  - use `dom_register_renderer_tests(<backend> <explicit_test> <caps_test>)`.

## Build number gating

- `dom_update_build_number` refreshes generated build number headers without bumping.
- `dom_bump_build_number` increments the global build number.
- `testx_all` runs `ctest` and then bumps the build number on success.

Use `cmake --build <build-dir> --target testx_all` to enforce the rule:
build number bumps only after tests pass.
