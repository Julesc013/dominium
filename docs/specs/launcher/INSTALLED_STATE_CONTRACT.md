Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Installed-State Contract (Launcher)

Note: This document describes the legacy DSU `installed_state.dsustate` used by
the current launcher CLI. The setup `installed_state.tlv` handoff is defined in
`docs/core/INSTALLED_STATE_CONTRACT.md`.

This document defines the launcher-facing contract for `installed_state.dsustate`.
The installed-state file is the authoritative record of a Dominium installation.

## Requirements (locked)

- The launcher must treat installed-state as authoritative.
- The launcher must refuse to run if the state is missing or invalid.
- The launcher must provide repair/verify instructions only (never install).
- The launcher must support a smoke-test mode.

## File location

Default location (relative to install root):

- `<install_root>/.dsu/installed_state.dsustate`

The launcher discovers the state by walking parent directories from the
executable location (max depth 3) and validating the first state found.

## Validation rules

The launcher must:

- load the state via Setup Core (`dsu_state_load`)
- validate with `dsu_state_validate`
- verify that the primary install root exists and matches the filesystem

Any failure results in refusal to launch.

## Recovery instructions

On failure, the launcher prints deterministic recovery steps:

1. `dominium-setup-legacy verify --state "<state_path>" --format json`
2. If verify reports issues:
   - `dominium-setup-legacy export-invocation --manifest <manifest> --state "<state_path>" --op repair --out repair.dsuinv`
   - `dominium-setup-legacy plan --manifest <manifest> --state "<state_path>" --invocation repair.dsuinv --out repair.dsuplan`
   - `dominium-setup-legacy apply --plan repair.dsuplan`

The launcher never performs install, repair, or uninstall actions directly.

## Smoke-test mode

The launcher provides smoke-test modes to validate installed-state and critical
runtime files without launching the full UI:

- `--smoke-test` (state-only)
- `--smoke-gui`
- `--smoke-tui`

Smoke tests must fail deterministically when installed-state is missing or invalid.

## See also

- `docs/setup_legacy/INSTALLED_STATE_SCHEMA.md`
- `docs/setup_legacy/CLI_REFERENCE.md`