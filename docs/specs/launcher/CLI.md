# Dominium Launcher CLI (Control Plane)

Doc Version: 1

This document specifies the stable, automation-friendly CLI for the launcher-as-control-plane model.

## Conventions

- A **command** is the first argv token that does not start with `-`.
- Output is **line-oriented** `key=value` (one per line), in a stable order per command.
- The recommended automation mode is headless: `--ui=null --gfx=null`.
- Unless explicitly stated, commands operate under `--home=<state_root>` (default `.`).

## Global Flags

- `--home=<path>`: state root (contains `instances/`, `exports/`, `tools_registry.tlv`, etc). Default: `.`.
- `--mode=gui|tui|cli|headless`: selects the front-end when no control-plane command is present.
- `--front=gui|tui|cli|headless`: alias for `--mode=...`.
- `--ui=native|dgfx|null`: selects the UI backend (headless mode uses `null`).
- `--gfx=<backend_id>`: selects the graphics backend id (headless mode uses `null`).

Note: `--ui` / `--gfx` influence backend selection and are recorded in audit; they do not change launcher core semantics.

## Smoke/Test Flags

These flags are side-effect free and do not invoke control-plane commands.

- `--smoke-test`: validates installed-state contract and critical paths; refuses to run if state is missing/corrupt.
- `--state <path>`: override installed-state path used by `--smoke-test`.
- `--smoke-gui`: minimal GUI boot smoke (renders a small frame and exits).
- `--smoke-tui`: minimal TUI boot smoke.

Exit codes for `--smoke-test`:
- `0`: success
- `3`: installed state missing/invalid
- `4`: installed state has zero components
- `5`: critical paths missing under install root

## Commands

### `list-instances`

Prints instance ids under `<state_root>/instances/`.

Args:
- none

Output:
- `result=ok|fail`
- `instances.count=<N>`
- `instances[i].id=<instance_id>` (0..N-1)

Example:
- `dominium-launcher --ui=null --gfx=null --home=state list-instances`

### `create-instance --template=<template_id>`

Creates a new instance by cloning a template instance id.

Args:
- `--template=<template_id>` (required)

Output:
- `result=ok|fail`
- `template_id=<template_id>`
- `instance_id=<new_instance_id>`

Example:
- `dominium-launcher --ui=null --gfx=null --home=state create-instance --template=tmpl0`

### `clone-instance <source_instance_id> [--new=<instance_id>]`

Clones an existing instance into a new instance root. If `--new` is not provided, the launcher chooses a deterministic id of the form:

`<source_instance_id>_clone<N>`

Args:
- `<source_instance_id>` (required)
- `--new=<instance_id>` (optional)

Output:
- `result=ok|fail`
- `source_id=<source_instance_id>`
- `instance_id=<new_instance_id>`
- on failure: `error=<code>` and optional `detail=<text>`

Example:
- `dominium-launcher --ui=null --gfx=null --home=state clone-instance inst0 --new=inst0_working_copy`

### `delete-instance <instance_id>`

Soft-deletes an instance by swapping in a tombstone and moving the previous live root under the instance `previous/` directory.

Args:
- `<instance_id>` (required)

Output:
- `result=ok|fail`
- `instance_id=<instance_id>`
- on failure: `error=<code>` and optional `detail=<text>`

Example:
- `dominium-launcher --ui=null --gfx=null --home=state delete-instance inst0_working_copy`

### `verify-instance <instance_id>`

Validates an instance deterministically using the prelaunch validation pipeline (no spawn required).

Args:
- `<instance_id>` (required)

Output:
- `result=ok|fail`
- `instance_id=<instance_id>`
- on failure: `error=verify_failed` and `detail=<text>`

Example:
- `dominium-launcher --ui=null --gfx=null --home=state verify-instance inst0`

### `export-instance <instance_id> --mode=definition|bundle`

Exports an instance under `<state_root>/exports/<instance_id>/`.

Args:
- `<instance_id>` (required)
- `--mode=definition|bundle` (required)

Output:
- `result=ok|fail`
- `instance_id=<instance_id>`
- `mode=definition|bundle`
- `export_root=<state_root>/exports/<instance_id>`

Example:
- `dominium-launcher --ui=null --gfx=null --home=state export-instance inst0 --mode=bundle`

### `import-instance <import_root>`

Imports an instance bundle from a directory containing `manifest.tlv`.

Args:
- `<import_root>` (required)

Output:
- `result=ok|fail`
- `import_root=<import_root>`
- `instance_id=<new_instance_id>`

Example:
- `dominium-launcher --ui=null --gfx=null --home=state import-instance state/exports/inst0`

### `launch <instance_id> --target=game|tool:<tool_id> [--keep_last_runs=<N>]`

Executes a launch attempt (game or tool). Always creates a per-run directory under the instance, even when refused.

Args:
- `<instance_id>` (required)
- `--target=game|tool:<tool_id>` (required)
- `--keep_last_runs=<N>` (optional; default `8`; `0` disables run cleanup)

Output (always present):
- `result=ok|fail`
- `instance_id=<instance_id>`
- `launch_target=game|tool:<tool_id>`
- `run_id=0x<16_hex_digits>`
- `run_dir=<state_root>/instances/<id>/logs/runs/<run_dir_id>`
- `handshake_path=<...>/handshake.tlv`
- `launch_config_path=<...>/launch_config.tlv`
- `selection_summary_path=<...>/selection_summary.tlv`
- `exit_status_path=<...>/exit_status.tlv`
- `audit_path=<...>/audit_ref.tlv`
- `refused=0|1`
- `spawned=0|1`
- `waited=0|1`
- on refusal: `refusal_code=<u32>` and `refusal_detail=<text>`
- on waited spawn: `child_exit_code=<i32>`
- on success: selection summary is printed as:
  - `selection_summary.line=<single_line>`
  - `selection_summary.*=<key/value lines>` (see `docs/launcher/ECOSYSTEM_INTEGRATION.md`)

Example (tool):
- `dominium-launcher --ui=null --gfx=null --home=state launch inst0 --target=tool:tool_manifest_inspector`

### `safe-mode <instance_id> --target=game|tool:<tool_id> [--keep_last_runs=<N>]`

Same as `launch`, but requests safe mode and forces offline-safe behavior for the run.

Args:
- `<instance_id>` (required)
- `--target=game|tool:<tool_id>` (required)
- `--keep_last_runs=<N>` (optional; default `8`; `0` disables run cleanup)

Example:
- `dominium-launcher --ui=null --gfx=null --home=state safe-mode inst0 --target=game`

### `audit-last <instance_id>`

Loads and prints the most recent run audit for an instance, plus the deterministic selection summary (from the audit embed or `selection_summary.tlv`).

Args:
- `<instance_id>` (required)

Output:
- `result=ok|fail`
- `instance_id=<instance_id>`
- `run_dir_id=<16_hex_digits>`
- `audit_path=<...>/audit_ref.tlv`
- `selection_summary_path=<...>/selection_summary.tlv`
- `audit.run_id=0x<16_hex_digits>`
- `audit.exit_result=<i32>`
- `audit.reasons.count=<N>`
- `audit.reasons[i]=<text>` (0..N-1)
- `selection_summary.line=<single_line>` and `selection_summary.*=<key/value lines>`

Example:
- `dominium-launcher --ui=null --gfx=null --home=state audit-last inst0`

### `diag-bundle <instance_id> --out=<dir>`

Exports a deterministic diagnostic bundle directory for an instance, including last-run artifacts when present.

Args:
- `<instance_id>` (required)
- `--out=<dir>` (required)

Output:
- `result=ok|fail`
- `instance_id=<instance_id>`
- `out=<dir>`
- optional: `last_run_id=<16_hex_digits>`

Bundle layout is specified in `docs/specs/launcher/ARCHITECTURE.md`.

Example:
- `dominium-launcher --ui=null --gfx=null --home=state diag-bundle inst0 --out=state/diag/inst0`

## Related Docs

- `docs/specs/launcher/ARCHITECTURE.md`
- `docs/launcher/ECOSYSTEM_INTEGRATION.md`
- `docs/launcher/TESTING.md`
