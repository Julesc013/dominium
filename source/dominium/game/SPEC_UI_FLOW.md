# Game UI Flow (dgfx IR / dui)

Status: draft
Version: 1

This document defines how the game renders the play flow using the existing
dgfx IR renderer and the dui UI system.

## 1. UI architecture rules
- The game UI is rendered through dgfx IR and dui widgets.
- UI state must not mutate the deterministic simulation directly.
- UI actions are translated into high-level commands or phase transitions.
- Runtime queries (read-only) may be used to display status.

## 1.1 Non-blocking execution
- The UI/render thread MUST NOT block on IO, decompression, or content loading.
- Progress indicators are derived and MUST NOT gate simulation.
- Missing data degrades fidelity rather than stalling rendering.
- See `docs/SPEC_NO_MODAL_LOADING.md` and `docs/SPEC_FIDELITY_DEGRADATION.md`.

## 2. Phase-driven screens
The UI is phase-driven (see `docs/SPEC_PLAY_FLOW.md`).

### PHASE_SPLASH
- Full-screen splash panel with title/logo and a spinner/progress stub.
- Shows non-authoritative progress (content ready, net ready, world init).
- Does not advance simulation.

### PHASE_MAIN_MENU
- Main menu panel:
  - Buttons: "Start Session (Host)", "Join Session", "Quit".
  - Fields: player name, server address/port.
- UI only sets selection data in the phase context.

### PHASE_SESSION_START
- Minimal "Starting session..." overlay.
- No direct sim mutation; only triggers net/session initialization.

### PHASE_SESSION_LOADING
- Non-blocking session transition overlay with readiness flags:
  - content loaded (yes/no)
  - net session ready (yes/no)
  - world init progress (stub % OK)
- Progress is derived; no blocking waits on IO or content loads.
- Optional transparent overlay:
  - enabled by `--ui.transparent-loading=1` when backend supports it.
  - fallback to opaque overlay if unsupported.

### PHASE_IN_SESSION
- Minimal HUD (instance id, seed, status).
- Uses existing dui widgets for debug/build tools.
- Pause/quit to menu handled via phase transitions.

### PHASE_SHUTDOWN
- No UI; perform shutdown and exit.

## 3. Input routing
- UI click handling is performed via dui widget hit-tests.
- Input that is not consumed by UI routes to camera controls and build tools.

## 4. Runtime queries used by UI
- instance id / seed
- net readiness state
- world tick count (optional)
- content readiness flags (non-authoritative)

## 5. Determinism notes
- UI timing (splash minimum, loading progress) is not authoritative.
- Sim ticks only advance in `PHASE_IN_SESSION` unless explicitly enabled.
