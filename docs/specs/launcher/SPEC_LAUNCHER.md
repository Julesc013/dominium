Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- None. This spec is implemented under `launcher/`.

GAME:
- None. This spec is implemented under `launcher/`.

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
# Dominium — Launcher Specification (Updated)

This launcher spec aligns with the multi-mode architecture described in `docs/LAUNCHER_SETUP_OVERVIEW.md`. The launcher is optional; runtimes remain runnable without it.

## Goals
- Discover installs via `dominium_install.json` manifests (portable/per-user/system).
- Persist lightweight launcher DB (`launcher/db.json`) with installs and profiles.
- Spawn supervised instances (client/server/tools) with launcher session/instance IDs.
- Provide CLI/TUI/GUI entrypoints (GUI/TUI may be stubbed but share the same core).
- Never link the deterministic engine; rely on runtime CLIs and manifests.

## Display and runtime contract
- Display enum: `none`, `cli`, `tui`, `gui`, `auto` (maps to `DomDisplayMode`).
- Launcher passes `--display=...`, `--role=...`, `--launcher-session-id`, and `--launcher-instance-id` to runtimes.
- Runtimes expose `--version` and `--capabilities` JSON endpoints and honour display mode selection. They must behave identically without launcher flags.

## Install handling
- Each install root carries `dominium_install.json` (schema_version 1). See `docs/FORMATS/FORMAT_INSTALL_MANIFEST.md`.
- Portable installs keep launcher data under the install root; per-user/system installs store launcher DB under user config roots.
- Repair/update flows are delegated to `dom_setup`; launcher does not mutate installs beyond reading manifests.

## CLI surface (summary)
- `installs list|info|repair`
- `instances start|list|stop`
- See `docs/API/LAUNCHER_CLI.md` for full flag details.

## Logging and supervision
- Log aggregation is minimal in the current stub (stdout/stderr via process handles). Future work can add ring buffers and log files per instance (`runtime_logs/<instance-id>.log`).
- Instance lifecycle is tracked in-memory per launcher session.

## Open extensions
- GUI/TUI layering on top of the core APIs.
- IPC between launcher and runtimes for richer presence/telemetry.
- Mod/profile management stored alongside the launcher DB.

## Related specs
- `docs/specs/SPEC_LAUNCH_HANDSHAKE_GAME.md`
- `docs/specs/SPEC_FS_CONTRACT.md`
- `docs/specs/SPEC_UNIVERSE_BUNDLE.md`