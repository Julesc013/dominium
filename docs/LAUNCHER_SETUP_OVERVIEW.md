# Dominium — Launcher & Setup Overview

This document summarizes how installs, the launcher, and runtimes fit together. It is an overview; detailed CLI contracts live under `docs/API/`.

## Install modes
- **portable** — fully self-contained under one directory; no registry writes; user data stays inside the install root unless overridden.
- **per-user** — binaries under user-local program directory; user data under user-local config/data roots.
- **system** — binaries under system roots (Program Files/`/Applications`/`/opt`); optional shared data root; user data still per-user.

Every install root contains `dominium_install.json` (see `docs/FORMATS/FORMAT_INSTALL_MANIFEST.md`) that records install ID, type, platform, version, timestamp, and origin.

## dom_setup (installer/repair/uninstaller)
- Commands: `install`, `repair`, `uninstall`, `list`, `info`.
- Responsibilities: create/verify/uninstall installs, write/read manifests, and register installs (registry/index file where allowed).
- OS helpers map defaults for per-user/system installs and user-data roots.
- Runs in C++98, cross-platform; prefers not to elevate. Portable installs avoid any system writes.

## dom_launcher (multi-mode launcher)
- Roles: discover installs from manifests + registry/index, manage profiles/mod sets, spawn supervised instances (client/server/tools), and aggregate runtime logs.
- UI modes: CLI, TUI, GUI (GUI/TUI may be stubbed; core logic is shared).
- Never links the engine or parses simulation internals; relies on runtime CLIs and metadata.
- Stores a launcher DB (`db.json`) in user-data (or install-local for portable) with installs, profiles, and recent instances.

## Runtimes and display modes
- Display enum: `none`, `cli`, `tui`, `gui`, `auto` (`auto` picks the best available mode).
- Runtimes expose:
  - `--version` → JSON (`binary_id`, `binary_version`, `engine_version`, `schema_version`).
  - `--capabilities` → JSON (roles, display modes, save/content versions).
  - `--display=...` → select frontend (NONE/CLI/TUI/GUI).
  - `--launcher-session-id`, `--launcher-instance-id` → optional tags for supervised runs.
  - `--launcher-integration=off` → force standalone behavior.
- Runtimes must behave identically without launcher flags; supervision is additive.

## Supervised vs standalone
- **Standalone**: user launches runtime directly; no launcher IDs; runtime still honours `--display` and `--role`.
- **Supervised**: launcher spawns runtime with session/instance IDs, aggregates logs, and tracks lifecycle/playtime. Repair/updates are delegated to `dom_setup`.

## Data locations (summary)
- Portable: everything under install root.
- Per-user: binaries under user programs dir; launcher DB/config under `%APPDATA%`/`$XDG_CONFIG_HOME`/`~/Library/Application Support`; user data under `%LOCALAPPDATA%`/`$XDG_DATA_HOME`/`~/Library/Application Support`.
- System: binaries under system dirs; user data still per-user; optional shared cache under `%PROGRAMDATA%` or `/usr/local/share`.
