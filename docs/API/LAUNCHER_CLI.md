# dom_launcher CLI

The launcher runs in CLI/TUI/GUI modes; CLI is the reference and shared with TUI/GUI. Commands rely on install manifests (`dominium_install.json`) and delegate install/repair to `dom_setup`.

## Top-level
- `dom_launcher --cli` (default), `dom_launcher --tui`, `dom_launcher --gui` (stub).

## Commands
- `installs list`  
  Discover installs via manifests, index file, and defaults. Prints `install_id | root | type | version`.
- `installs info --install-id=<id>`  
  Prints manifest fields for the given install.
- `installs repair --install-root=<path>`  
  Calls `dom_setup repair` on the provided root.

- `instances start --install-id=<id> [--exe=<path>] [--role=client|server|tool] [--display=gui|tui|cli|none]`  
  Spawns a runtime with launcher session/instance IDs and passes through display/role flags. Defaults `exe` to `<install>/bin/dom_cli`.
- `instances list`  
  Lists instances started in the current launcher session.
- `instances stop --id=<instance-id>`  
  Terminates a tracked instance.

## Data
- Launcher DB: `launcher/db.json` under user config root (or install-local for portable installs). Stores installs and profiles (schema_version `1`).
- Install discovery uses `dom_setup` path helpers and `dominium_install.json`.

See `docs/LAUNCHER_SETUP_OVERVIEW.md` for overall architecture.
