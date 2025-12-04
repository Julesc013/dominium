# Dominium — Launcher Specification (V1)

Purpose: a minimal, always-available entrypoint that brings up configuration UI and spawns the appropriate client/server binaries. The launcher never affects simulation state and always runs in the safest render mode.

## Platform and renderer
- Launcher binaries (per-OS):
  - Windows: `dom_launcher-win32-software.exe` (DOM_PLATFORM=WIN32, DOM_RENDER_BACKEND=SOFTWARE)
  - Linux/Posix (SDL2 over X11/Wayland): `dom_launcher-posix-sdl2-software` (DOM_PLATFORM=SDL2, DOM_RENDER_BACKEND=SOFTWARE)
  - macOS: `dom_launcher-macosx-software` (DOM_PLATFORM=MACOSX, DOM_RENDER_BACKEND=SOFTWARE)
- Render mode: `DOM_RENDER_MODE_VECTOR_ONLY` by default (CAD-style UI, deterministic placeholders).
- Headless flag: `DOM_HEADLESS=0` (launchers are always headful).

## Relationship to client/server
- Launchers share the same platform/render abstractions as engine/game.
- They never touch simulation; only configuration, asset validation, and process spawning.
- Clients/servers are separate binaries per platform+renderer combination (see BUILDING.md).
- The `dominium` script resolves to the correct launcher binary for the current OS and exports `DOM_PLATFORM`, `DOM_RENDER_BACKEND`, and `DOM_HEADLESS`.

## CLI/env contract (summary)
- Environment:
  - `DOM_PLATFORM` — platform backend (WIN32, MACOSX, SDL2, etc.).
  - `DOM_RENDER_BACKEND` — renderer (SOFTWARE for launcher).
  - `DOM_HEADLESS` — must be 0 for launchers.
- Args: forwarded verbatim to the launcher binary for future configuration flags.

## Safety and determinism
- Launcher visuals may be non-deterministic; they must not change sim state.
- Renderer is software-only with vector UI to maximize compatibility and reduce GPU variance.
