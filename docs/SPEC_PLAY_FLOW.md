--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- None. Engine provides generic primitives only if referenced.

GAME:
- Rules, policy, and interpretation defined by this spec.
- Implementation lives under `game/` (rules/content/ui as applicable).

TOOLS:
- None. Tools may only consume public APIs if needed.

SCHEMA:
- None (no canonical schema formats defined here).

FORBIDDEN:
- No launcher/setup orchestration logic in engine or game.
- No engine internal headers exposed outside engine targets.
- No game rules or policy implemented inside engine primitives.

DEPENDENCIES:
- Engine -> libs/ and schema/ only (never game/launcher/setup/tools).
- Game -> engine public API and schema/ only.
- Tools -> engine public API, game public API, and schema/ only.
- Launcher/Setup (if applicable) -> libs/contracts + schema (launcher may also use engine public API).
--------------------------------
# Play Flow (Launcher ↔ Game)

Status: draft
Version: 1

This spec defines the canonical end-to-end "play the game" flow, the game-side
phase/state contract, and launcher behavior when starting a run. It is
authoritative for user-facing flow and refusal behavior.

## 1. Canonical user flow (steps 1–8)
1) Open launcher.
2) Launch an instance.
3) Launcher minimizes or closes (policy-controlled).
4) Game window opens.
5) Splash/loading screen.
6) Main menu/title screen.
7) Start or join a session.
8) Session loading screen (optionally transparent window into loading),
   then in-session.

## 2. Launcher policy: post-launch behavior
Launcher behavior after spawning the game is configurable:
- `launcher_launch_behavior = minimize | close | stay`
- `minimize`: keep launcher running, minimize window.
- `close`: gracefully close launcher after successful game spawn.
- `stay`: keep launcher visible and running.

The launcher remains the control plane. It must not mutate simulation state or
content; it only prepares launch inputs and spawns the game.

## 3. Game phases (authoritative)
Game phases are authoritative in the game runtime:
- `PHASE_BOOT`
- `PHASE_SPLASH`
- `PHASE_MAIN_MENU`
- `PHASE_SESSION_START`
- `PHASE_SESSION_LOADING`
- `PHASE_IN_SESSION`
- `PHASE_SHUTDOWN`

Phases are explicit, logged, and only advance via defined transitions.

## 4. Headless / automation mode
Headless mode runs the same phase machine without opening a window:
- `--mode=headless` selects the headless frontend and defaults the system backend to `null`.
- Headless auto-starts host unless `--connect` is provided (join).
- `--auto-host` forces an automatic host start (useful for scripted runs).
- `--headless-ticks=<u32>` exits after N in-session ticks (smoke/CI).
- `--headless-local=1` runs a local single-player session without binding sockets.
- `--dev-allow-missing-content=1` allows empty content packs for dev/test only (logged).

## 5. Filesystem and handshake constraints
- Handshake TLV contains no absolute paths.
- All filesystem access resolves through launcher-defined roots:
  - `DOMINIUM_RUN_ROOT` (preferred; per-run writable root).
  - `DOMINIUM_HOME` (allowed; logical instance/content root).
- Launcher sets `DOMINIUM_RUN_ROOT` per run and passes `--handshake=handshake.tlv`
  relative to it; `DOMINIUM_HOME` is set when available.
- The game refuses launcher mode runs if required roots are missing or invalid.
- Refusals are written to `DOMINIUM_RUN_ROOT/refusal.tlv` if available; otherwise
  stderr only. See `docs/SPEC_FS_CONTRACT.md`.

## 6. Refusal points
Refusals can occur at:
- handshake load/parse/validation (invalid or missing fields),
- missing/invalid run/home roots,
- path traversal or absolute path inputs in launcher mode,
- content graph validation failures.

Refusals surface via:
- `refusal.tlv` (run root) and stderr logs.

## 7. Timing goals (non-binding)
These are UX targets and do not affect determinism:
- Splash minimum duration: 750–1500 ms (configurable; non-blocking).
- Headless automation uses a shorter minimum to keep tests fast.
- Loading screens may advance as soon as required readiness signals are true.
- Background loading tasks must not mutate deterministic sim state.

## 8. Phase transition summary
```
BOOT -> SPLASH -> MAIN_MENU
MAIN_MENU -> SESSION_START -> SESSION_LOADING -> IN_SESSION
IN_SESSION -> MAIN_MENU (quit to menu)
Any phase -> SHUTDOWN (fatal error or explicit quit)
```

## 9. Related specs
- `docs/SPEC_FS_CONTRACT.md`
- `docs/SPEC_LAUNCH_HANDSHAKE_GAME.md`
- `docs/SPEC_GAME_CLI.md`
