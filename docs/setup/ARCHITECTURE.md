# Dominium Setup Architecture (Setup2)

This document describes the setup2 architecture and how it reuses the shared
core libraries.

## Layers

- Kernel (`dsk_kernel`): deterministic orchestration and contracts only. No OS
  headers, no UI dependencies, no side effects.
- Services (`dss_services`): side effects behind C ABI facades (filesystem,
  permissions, process, providers).
- Frontends (CLI/TUI/GUI/adapters): UI, argument parsing, and output wiring.

## Shared Core Libraries

Setup2 reuses the shared core modules defined in `docs/core/CORE_LIBRARIES.md`:
TLV/schema, err_t, structured logs, job engine, caps/solver, audit helpers,
providers, and installed_state parsing/writing.

## Handoff Artifacts

Setup2 emits versioned TLV artifacts for external consumption:

- `install_manifest.tlv`
- `install_request.tlv`
- `install_plan.tlv`
- `installed_state.tlv`
- `setup_audit.tlv`

See `docs/setup2/` for the schemas and invariants.
