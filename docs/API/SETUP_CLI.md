# dom_setup CLI

`dom_setup` owns install creation, repair, uninstall, and discovery. It writes `dominium_install.json` into every install root and optionally records installs in a per-user index file.

## Commands
- `install --mode=portable|per-user|system --target=<path> [--version=X.Y.Z]`  
  Creates an install at the target path (or OS default when omitted for per-user/system). Writes `dominium_install.json` (schema_version `1`) and prepares minimal layout (`bin/`, `data/`, `mods/`, `launcher/`).
- `repair --install-root=<path>`  
  Validates manifest presence and recreates minimal layout/placeholder files.
- `uninstall --install-root=<path> [--remove-user-data]`  
  Removes install root; optionally removes user-data root for the install type.
- `list`  
  Scans default roots and the current working directory for manifests and prints a summary.
- `info --install-root=<path>`  
  Prints manifest fields for a specific install.

## Paths and modes
- Portable: install and user data stay under the target directory.
- Per-user: defaults to `%LOCALAPPDATA%/Dominium/Programs` (Windows), `$XDG_DATA_HOME/dominium` (Linux), `~/Applications/Dominium` (macOS).
- System: defaults to `%ProgramFiles%/Dominium`, `/opt/dominium`, `/Applications/Dominium.app`.
- User data roots: `%LOCALAPPDATA%/Dominium`, `$XDG_DATA_HOME/dominium`, `~/Library/Application Support/Dominium` (portable uses install root).
- Install index (best effort): user config root `install_index.json`.

## Exit codes
- `0` success.
- `1` on validation or IO failure (missing manifest, permission issues, unsupported mode).

See `docs/FORMATS/FORMAT_INSTALL_MANIFEST.md` for manifest structure and `docs/LAUNCHER_SETUP_OVERVIEW.md` for the overall system design.
