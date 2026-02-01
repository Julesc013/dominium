Status: HISTORICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: docs/architecture/CANON_INDEX.md

This document is archived.
Reason: Superseded by docs/architecture/CANON_INDEX.md.
Do not use for implementation.

This document is archived.
Reason: Superseded by docs/architecture/CANON_INDEX.md.
Do not use for implementation.

This document is archived.
Reason: Superseded by unknown.
Do not use for implementation.

# ARCHIVED: Launcher Audit Snapshot (Phase 0)

Archived: point-in-time audit.
Reason: Historical snapshot; current launcher specs supersede it.
Superseded by:
- `docs/specs/launcher/ARCHITECTURE.md`
- `docs/specs/launcher/SPEC_LAUNCHER.md`
Still useful: background on early launcher audit notes.

# Launcher Audit Snapshot (Phase 0)

Date: 2026-01-17

This file records the current launcher implementation state as observed in the repository.
It does not judge correctness. It lists responsibilities, inputs/outputs, and limitations based on existing files.

## Responsibilities (as implemented today)
- Public launcher API contracts are defined in `launcher/include/launcher/*.h`.
- Launcher core implementation is stubbed in `launcher/core/launcher_core.c` and related stub files.
- Launcher CLI entrypoint is implemented as a stub command dispatcher in `launcher/cli/launcher_cli_main.c`.
- Launcher GUI and TUI entrypoints are stub programs in `launcher/gui/launcher_gui_stub.c` and `launcher/tui/launcher_tui_stub.c`.
- Internal launcher contracts and state models exist in:
  - `launcher/include/launcher/_internal/launcher_internal/*.h`
  - `launcher/include/launcher/_internal/dom_launcher/*.h`
- Build targets are declared in `launcher/CMakeLists.txt`:
  - `launcher_core` (alias `launcher::launcher`)
  - `launcher_cli` (alias `launcher::cli`)
  - `launcher_gui` (alias `launcher::gui`)
  - `launcher_tui` (alias `launcher::tui`)

## Inputs
- CLI arguments for `launcher` executable:
  - `--help`, `-h`, `--version`, `version`, `list-profiles` in `launcher/cli/launcher_cli_main.c`.
- Launcher core API inputs:
  - `launcher_init(const launcher_config* cfg)` in `launcher/include/launcher/launcher.h`.
  - `launcher_config_load/save` in `launcher/include/launcher/launcher_config.h`.
  - `launcher_profile_*` in `launcher/include/launcher/launcher_profile.h`.
  - `launcher_mods_*` in `launcher/include/launcher/launcher_mods.h`.
  - `launcher_process_*` in `launcher/include/launcher/launcher_process.h`.
- Internal launcher contracts consume dom_contracts headers:
  - `dom_contracts/dom_shared/manifest_install.h` in
    `launcher/include/launcher/_internal/launcher_internal/launcher_context.h` and
    `launcher/include/launcher/_internal/dom_launcher/launcher_context.h`.
  - `dom_contracts/dom_shared/json.h` in
    `launcher/include/launcher/_internal/launcher_internal/launcher_db.h`.

## Outputs
- CLI stdout messages:
  - Usage, version, and profile listings in `launcher/cli/launcher_cli_main.c`.
- GUI/TUI stdout stubs:
  - `launcher gui stub` and `launcher tui stub` from stub entrypoints.
- Return codes:
  - CLI returns `0` on handled commands, `2` on unknown command in `launcher/cli/launcher_cli_main.c`.
  - Core stub functions return fixed values (mostly `0` or `-1`) in `launcher/core/*.c`.

## Known Limitations (observed)
- Core modules in `launcher/core/{discover,profile,invoke}` are empty directories.
- Core implementations are stubbed:
  - `launcher/core/launcher_core.c` does not perform initialization or run logic.
  - `launcher/core/launcher_config_stub.c` always returns failure for load/save.
  - `launcher/core/launcher_profile_stub.c` reports zero profiles and failure to save/set active.
  - `launcher/core/launcher_mods_stub.c` reports zero mods and failure to set enabled.
  - `launcher/core/launcher_process_stub.c` does not spawn or manage processes.
- Platform adapter directories exist but are empty:
  - `launcher/platform/{bsd,linux,mac,win}` and subdirectories.
- UI directory exists but is empty: `launcher/ui`.