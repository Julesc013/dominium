# dom_launcher CLI

The launcher runs in CLI/TUI/GUI modes. CLI is the canonical entrypoint and is
shared with TUI/GUI intent APIs.

Install and instance management are delegated to the OPS CLI
(`tools/ops/ops_cli.py`) via the `ops` command. The OPS CLI returns structured
compatibility reports and refusal payloads.

## Top-level
- `dom_launcher --ui=none|tui|gui` (default: CLI with `--ui=none`).

## Commands
- `version`  
  Show launcher version.
- `list-profiles`  
  List known profiles.
- `capabilities`  
  Report platform + renderer availability.
- `new-world`  
  Create a new world (template-driven; may be unavailable).
- `load-world`  
  Load a world save (may be unavailable).
- `inspect-replay`  
  Inspect a replay (may be unavailable).
- `ops <args>`  
  Pass-through to OPS CLI for install/instance enumeration and lifecycle:
  `installs list`, `instances list`, `instances create`, `instances clone`,
  `instances fork`, `instances activate`.
- `share <args>`  
  Pass-through to share CLI for bundle export/import/inspect:
  `export`, `inspect`, `import`.
- `tools`  
  Open tools shell (handoff).
- `settings`  
  Show current UI settings.
- `exit`  
  Exit launcher.

## Data & contracts
- Install manifest: `install.manifest.json` (`schema/install.manifest.schema`).
- Instance manifest: `instance.manifest.json` (`schema/instance.manifest.schema`).
- Ops transactions: `docs/architecture/OPS_TRANSACTION_MODEL.md`.
- Install/instance model: `docs/architecture/INSTALL_MODEL.md`,
  `docs/architecture/INSTANCE_MODEL.md`.
- Launcher/setup contract: `docs/distribution/LAUNCHER_SETUP_CONTRACT.md`.
