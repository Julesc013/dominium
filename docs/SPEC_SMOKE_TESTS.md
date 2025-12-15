# Smoke Tests (GUI + System)

This document defines the deterministic-safe smoke test contract for:

- `dominium-launcher.exe --smoke-gui`
- `dominium-game.exe --smoke-gui`

These modes exist to validate the platform window/event loop (`dsys`), renderer
selection/capability registry, and minimal immediate-mode UI drawing (`dgfx`)
without requiring audio, network, or game content.

## Goals

- Deterministic-safe: animation driven only by integer frame/tick counters.
- Bounded: completes quickly and cannot hang CI.
- Minimal: draws only a few primitives; no UI toolkit dependency.
- Auditable: prints required selection/build/schema metadata to logs.

## CLI Contract

### Flags

Both launcher and game accept:

- `--smoke-gui` — run the bounded GUI smoke loop and exit.
- `--gfx=<backend>` — choose graphics backend (selection audit is required).
- `--profile=<name>` — optional; used for canonical build matrix runs.
- `--print-selection` — optional; implied by `--smoke-gui`.
- `--lockstep-strict=<0|1>` — optional; see determinism requirements below.

### Frame/time bounds

Default bounds for `--smoke-gui`:

- Run for **at most 120 frames**, OR
- **~2 seconds wall-clock maximum**, whichever happens first.

Pressing **ESC** must terminate early with success (exit code 0).

### Required stdout/stderr lines

`--smoke-gui` must print the following (ordering is not strictly specified, but
each line must appear exactly once on success):

- Build identification: a stable build id and the current git commit hash.
- Simulation schema identification: a stable schema id for the sim-facing API.
- Selection audit: the same output as `--print-selection` (implied by smoke).
- Capability summary for the selected renderer/backend (from the capability
  registry used by selection).

### Exit codes

- `0` — success (completed bounded loop or exited early via ESC).
- Non-zero — failure to initialize platform, initialize gfx, or run the loop.

## Launcher: `dominium-launcher.exe --smoke-gui`

Smoke GUI for the launcher must:

- Create a platform window via `dsys` (win32).
- Initialize `dgfx` using the selected backend (from the selection registry).
- Render a minimal UI frame each iteration:
  - background clear
  - at least 3 button-like rectangles
  - a highlight rectangle that changes deterministically with the frame counter
- Pump platform events each frame.
- Not require audio or any network access.

## Game: `dominium-game.exe --smoke-gui`

Smoke GUI for the game must:

- Create a platform window via `dsys` (win32).
- Initialize `dgfx` using the selected backend (from the selection registry).
- Run a deterministic fixed-tick loop for the bounded duration.
- Render each iteration:
  - background clear
  - simple HUD panel rectangle(s)
  - a moving primitive driven only by integer tick counter (no floats)
- Pump platform events each frame.
- Not require audio or any network access.

## Determinism requirements

- `--gfx=soft` is required to pass and is determinism grade **D0** compatible.
- `--gfx=dx9` is optional and determinism grade **D2** compatible (visual-only).
- If `--lockstep-strict=1` is set, GUI smoke must not select a D2 renderer for
  simulation runs; it must either force `soft` for rendering or use a headless
  path while still validating selection/initialization where possible.

## Related docs

- `docs/SPEC_DETERMINISM.md`
- `docs/SPEC_DETERMINISM_GRADES.md`
- `docs/SPEC_CAPABILITY_REGISTRY.md`
- `docs/BUILD_MATRIX.md`
- `docs/SPEC_LAUNCHER_GUI.md`
