# dom_setup CLI

`dom_setup` owns install creation, repair, uninstall, and discovery. It writes `dominium_install.json` into every install root. The tool is plugin-ready (install profiles/hooks) and keeps setup logic outside the engine.

## Commands
- `install --mode=portable|per-user|system --install-root=PATH --version=X.Y.Z [--no-shortcuts] [--no-register-system] [--config=FILE] [--non-interactive]`  
  Creates an install (defaults: per-user mode, per-user install root). Writes `dominium_install.json` and builds minimal layout (`bin/`, `data/`, `mods/`, `launcher/`). Portable installs are self-contained and skip registration/shortcuts.
- `repair --install-root=PATH`  
  Validates manifest presence and restores registration/shortcuts; future work can add file verification.
- `uninstall --install-root=PATH [--remove-user-data]`  
  Removes install root; optionally removes user-data tied to this install (conservative).
- `list`  
  Scans default roots (per-user/system/portable) for manifests and prints a summary.
- `info --install-root=PATH`  
  Prints manifest fields for a specific install (JSON one-liner).

## Paths and modes
- Portable: install and user data stay under the target directory; no system registration or shortcuts.
- Per-user defaults: `%LOCALAPPDATA%/Dominium/Programs` (Windows), `$XDG_DATA_HOME/dominium` (Linux), `~/Applications/Dominium` (macOS).
- System defaults: `%ProgramFiles%/Dominium`, `/opt/dominium`, `/Applications/Dominium.app`.
- User data roots: `%LOCALAPPDATA%/Dominium`, `$XDG_DATA_HOME/dominium`, `~/Library/Application Support/Dominium` (portable uses install root).

## Exit codes
- `0` success.
- `1` on validation or IO failure (missing manifest, permission issues, unsupported mode).

See `docs/FORMATS/FORMAT_INSTALL_MANIFEST.md` for manifest structure and `docs/LAUNCHER_SETUP_OVERVIEW.md` for the overall system design.
