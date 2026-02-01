Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Runtime CLI Contract

Applies to runtime binaries such as `dom_main` (new entry), `dom_cli` (headless), and `dom_sdl` (UI placeholder). Runtimes remain functional when launched directly; launcher-specific flags are optional.

## Common flags (dom_main)
- `--version`  
  Prints JSON: `schema_version`, `binary_id`, `binary_version`, `engine_version`. Exits immediately.
- `--capabilities`  
  Prints JSON: `schema_version`, `binary_id`, `binary_version`, `engine_version`, `roles`, `supported_display_modes`, `supported_save_versions`, `supported_content_pack_versions`. Exits immediately.
- `--display=none|cli|tui|gui|auto`  
  Selects frontend; `auto` chooses GUI/TUI/CLI/none based on environment.
- `--role=client|server|tool`  
  Runtime role hint.
- `--universe=<path>`  
  Universe/save path for the run (required for actual gameplay).
- `--launcher-session-id=<GUID>` / `--launcher-instance-id=<GUID>`  
  Optional IDs from launcher supervision.
- `--launcher-integration=auto|off`  
  `off` ignores launcher IDs; `auto` (default) logs them if provided.
- `--help` / `-h`  
  Prints usage.

## dom_cli specifics
- Supports `--universe=<path>`, `--ticks=<N>`, `--surface=<id>` (existing flow).
- `--display=none` runs a stub path and exits successfully without ticking the engine.
- JSON output uses schema_version `1`.

Refer to `docs/FORMATS/FORMAT_INSTALL_MANIFEST.md` for install metadata used by launchers and setup tools.