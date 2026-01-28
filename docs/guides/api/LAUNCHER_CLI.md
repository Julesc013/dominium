# dom_launcher CLI

The launcher runs in CLI/TUI/GUI modes; CLI is the reference and shared with TUI/GUI.
Commands rely on install manifests (`install.manifest.json`). Legacy
`dominium_install.json` is supported as an adapter only. Install/repair is
delegated to `dom_setup`.

## Top-level
- `dom_launcher --cli` (default), `dom_launcher --tui`, `dom_launcher --gui` (stub).

## Commands
- `installs list`  
  Discover installs via manifests under default roots and manual paths. Prints `install_id | type | platform | root`.
- `installs add-path --path=PATH`  
  Adds a manual install root to the DB for discovery.

- `instances start --install-id=<id> [--role=client|server|tool] [--display=gui|tui|cli|none] [--universe=PATH]`  
  Spawns a supervised runtime (stubbed process in current build) with launcher session/instance IDs and display/role flags.
- `instances list`  
  Lists instances started in the current launcher session.
- `instances stop --instance-id=<id>`  
  Stops a tracked instance (stub termination in current build).

- `plugins list`  
  Lists registered plugins (stub until plugins are loaded).

## Data
- Launcher DB: `launcher/db.json` under user config root (or install-local for portable installs). Stores installs and profiles (schema_version `1`).
- Install discovery uses `dom_setup` path helpers and `dominium_install.json`.
- Manual install paths from the DB are added to discovery.

See `docs/LAUNCHER_SETUP_OVERVIEW.md` for overall architecture.
