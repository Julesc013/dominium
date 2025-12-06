# Runtime CLI Contract

Applies to runtime binaries such as `dom_cli` (headless), `dom_sdl` (UI placeholder), and future GUIs. Runtimes remain functional when launched directly; launcher-specific flags are optional.

## Common flags
- `--version`  
  Prints JSON: `schema_version`, `binary_id`, `binary_version`, `engine_version`. Exits immediately.
- `--capabilities`  
  Prints JSON: `schema_version`, `binary_id`, `binary_version`, `engine_version`, `roles`, `supported_display_modes`, `supported_save_versions`, `supported_content_pack_versions`. Exits immediately.
- `--display=none|cli|tui|gui|auto`  
  Selects the frontend. `auto` picks the best available mode. `none` runs headless.
- `--role=client|server|tool`  
  Runtime role hint (logged only for now).
- `--launcher-session-id=<GUID>` / `--launcher-instance-id=<GUID>`  
  Optional IDs passed by the launcher for logging and tagging. Ignored if absent.
- `--launcher-integration=off`  
  Explicitly ignore launcher IDs (reserved; current runtimes are integration-neutral).

## dom_cli specifics
- Supports `--universe=<path>`, `--ticks=<N>`, `--surface=<id>` (existing flow).
- `--display=none` runs a stub and exits successfully without ticking the engine.
- JSON output uses schema_version `1`.

Refer to `docs/FORMATS/FORMAT_INSTALL_MANIFEST.md` for install metadata used by launchers and setup tools.
