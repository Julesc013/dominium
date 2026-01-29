# dom_setup CLI

`dom_setup` prepares install roots and exposes OPS pass-through commands. It
does not mutate simulation state.

## Commands
- `version`  
  Show setup version.
- `status`  
  Show setup status.
- `prepare --root <path>`  
  Create an empty install layout at the given root (minimal directories only).
- `ops <args>`  
  Pass-through to OPS CLI for install/instance management. Use for:
  `installs list`, `instances list`, `instances create`, `instances clone`,
  `instances fork`, `instances activate`.
- `share <args>`  
  Pass-through to share CLI for bundle export/import/inspect:
  `export`, `inspect`, `import`.

## Data & contracts
- Install manifest: `install.manifest.json` (`schema/install.manifest.schema`).
- Instance manifest: `instance.manifest.json` (`schema/instance.manifest.schema`).
- Ops transactions: `docs/architecture/OPS_TRANSACTION_MODEL.md`.
- Install/instance model: `docs/architecture/INSTALL_MODEL.md`,
  `docs/architecture/INSTANCE_MODEL.md`.
- Launcher/setup contract: `docs/distribution/LAUNCHER_SETUP_CONTRACT.md`.
