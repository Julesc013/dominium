Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Setup Handoff (Launcher)

The launcher consumes Setup `installed_state.tlv` and imports legacy state when required.

## State discovery
- Default state path: `<install_root>/.dsu/installed_state.tlv`
- Legacy fallback: `<install_root>/.dsu/installed_state.dsustate`
- When run without `--state`, the launcher probes up to three parent directories from the executable.

## Import behavior
- If Setup state is missing but legacy state exists, the launcher calls `dsk_import_legacy_state`.
- Import audit is written to `<install_root>/.dsu/setup_audit.tlv`.
- Import is deterministic and read-only on legacy state.

## CLI integration
- `--state <path>` overrides the state path for smoke tests and diagnostics.
- `--smoke-test` validates state, install root, and critical binaries.

## Failure handling
- Corrupt state or missing install roots are refused with a recovery message.
- Recovery suggests:
  - `dominium-setup verify --state <state>`
  - `dominium-setup import-legacy-state --in <legacy_state> --out <state>`