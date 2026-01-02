# Dominium Setup Architecture (Setup)

This document describes the setup architecture and how it reuses the shared
core libraries.

## Layers

- Kernel (`dsk_kernel`): deterministic orchestration and contracts only. No OS
  headers, no UI dependencies, no side effects.
- Services (`dss_services`): side effects behind C ABI facades (filesystem,
  permissions, process, providers).
- Frontends (CLI/TUI/GUI/adapters): UI, argument parsing, and output wiring.

## Shared Core Libraries

Setup reuses the shared core modules defined in `docs/core/CORE_LIBRARIES.md`:
TLV/schema, err_t, structured logs, job engine, caps/solver, audit helpers,
providers, and installed_state parsing/writing.

## Handoff Artifacts

Setup emits versioned TLV artifacts for external consumption:

- `install_manifest.tlv`
- `install_request.tlv`
- `install_plan.tlv`
- `installed_state.tlv`
- `setup_audit.tlv`

See `docs/setup/` for the schemas and invariants.
