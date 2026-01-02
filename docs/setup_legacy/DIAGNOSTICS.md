# DIAGNOSTICS

Setup frontends share the structured logging model (`core_log`) and error taxonomy (`err_t`) with the launcher. Diagnostics should be produced as deterministic bundles using the same TLV conventions:

- Structured events are emitted with stable numeric fields only.
- No UI text, no environment variables, no machine identifiers.
- Paths are redacted unless they are safely relative to the setup state root.

When setup bundles are generated, they should mirror the launcher bundle layout:
- `bundle_meta.tlv` + `bundle_index.tlv`
- recent audit TLVs
- setup state manifests/plans
- structured event logs (per-run or per-session)

## Setup CLI logging
`dominium-setup` supports optional structured log output for kernel runs:
- `dominium-setup run ... --out-log <file>` writes `core_log` TLV events for each kernel stage.
- Events use `CORE_LOG_DOMAIN_SETUP` and `CORE_LOG_OP_SETUP_*` operation IDs.

This document exists to keep setup diagnostics aligned with the launcher bundle format.
