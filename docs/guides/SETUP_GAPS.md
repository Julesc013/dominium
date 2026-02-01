Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Dominium Setup Gaps (Phase A)

This document inventories current setup-related code and highlights gaps, stubs,
implicit formats, and contract mismatches that must be resolved before freezing
the setup baseline.

## Inventory

### Core (fetch/verify/install/rollback)
- Kernel entry: `setup/core/dsk_setup_core.c` (stub; returns fixed version/status).
- Core subdirectories present but empty:
  - `setup/core/fetch/`
  - `setup/core/install/`
  - `setup/core/verify/`
  - `setup/core/rollback/`
  - `setup/core/repair/`
  - `setup/core/uninstall/`
- Public kernel header: `setup/include/dsk/dsk_setup.h` (stub API only).
- Internal CLI/setup contract header:
  - `setup/include/dsu/_internal/dom_setup/dom_setup_config.h` (declares CLI
    parsing, config file load, and run_* functions; no implementation in setup/).

### Platform adapters
- Directory structure exists but no code:
  - `setup/platform/win/winnt/`
  - `setup/platform/win/win9x/`
  - `setup/platform/linux/`
  - `setup/platform/mac/osx/`
  - `setup/platform/mac/classic/`
  - `setup/platform/bsd/`

### UI frontends
- CLI: `setup/cli/setup_cli_main.c` (stub; only `version` and `status`).
- GUI: `setup/gui/dsu_gui_stub.c` (stub).
- TUI: `setup/tui/dsu_tui_stub.c` (stub).
- `setup/ui/` exists but empty.
- Frontend API: `setup/include/dsu/dsu_frontend.h` (stub API only).

### Packaging scripts
- Scripts and tooling under `setup/packages/scripts/`:
  - Packaging pipeline: `setup/packages/scripts/packaging/pipeline.py`
  - Manifest tooling: `setup/packages/scripts/packaging/dsumanifest.py`
  - Deterministic archives: `setup/packages/scripts/packaging/make_deterministic_archive.py`
  - Packaging targets: `setup/packages/scripts/packaging/{windows,linux,macos}/`
  - CI gates: `setup/packages/scripts/setup/*`, `setup/packages/scripts/release/*`
  - Repro checks: `setup/packages/scripts/repro/verify_reproducible_builds.py`

### Tests
- `setup/tests/` is empty.
- Integration test referencing setup contracts:
  - `game/tests/tests/dominium_integration/setup_flow_test.cpp` (calls
    `run_install`, `run_repair`, `run_uninstall`, `run_info` from
    `dom_setup_config.h`).
- Packaging validation tests exist under
  `setup/packages/scripts/packaging/tests/`.

### Legacy setup implementation
- Legacy setup code exists under `legacy/setup_core_setup/` with CLI adapters and
  core `run_*` implementations referenced by `dom_setup_config.h`.

## Incomplete or stubbed behavior
- Core setup functionality is stubbed; no planning/execution/rollback logic in
  `setup/core/`.
- CLI provides only `version` and `status`; no install/verify/repair/uninstall.
- GUI/TUI are stubs and do not call kernel APIs.
- Platform adapter folders exist without OS service implementations.
- `setup/tests/` has no coverage for required scenarios.
- Public setup API in `libs/contracts/include/dom_contracts/setup_api.h` has no
  implementation under `setup/`.

## Undocumented or implicit formats
- `dom_setup_config.h` states a JSON config file is supported, but no schema or
  parsing implementation exists in `setup/`.
- Setup-related TLV docs exist under `docs/setup/TLV_*.md`, yet there is no
  corresponding `schema/setup/` directory to formalize these formats.
- Packaging manifest tooling (`dsumanifest.py`, `pipeline.py`) emits/consumes
  manifest data without schema files in `schema/setup/`.

## Unreferenced or stranded code paths
- `setup/include/dsu/_internal/dom_setup/dom_setup_config.h` functions are not
  implemented in `setup/` and only exist in `legacy/setup_core_setup/`.
- `game/tests/tests/dominium_integration/setup_flow_test.cpp` targets the legacy
  setup API surface but has no active setup core to execute against.

## Intentionally deferred (known but not implemented here)
- No explicit deferral list exists in code; all missing core functionality and
  schemas appear to be pending implementation.

## Spec/contract mismatches or violations
- Setup schemas are absent under `schema/setup/` despite documentation and
  packaging tools describing structured setup artifacts.
- Public setup API surfaces conflict or drift:
  - `setup/include/dsk/dsk_setup.h` vs
    `libs/contracts/include/dom_contracts/setup_api.h` (two different public
    entrypoints; only stubs exist under setup/).
- UI frontends are not wired to kernel APIs, violating the requirement that UI
  be thin shells.