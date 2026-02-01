Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Application Contracts (Summary)

Scope: application-layer contracts used by setup/launcher/client/server/tools.

This document summarizes contract headers under:
- `libs/contracts/include/dom_contracts/`

## Contract headers
- `app_launch_request.h` — launch intent and parameters (POD).
- `app_launch_result.h` — launch result summary (POD).
- `app_instance_manifest.h` — instance identity and lineage (POD).
- `app_pack_state.h` — pack state, provenance, compatibility (POD).
- `app_capabilities.h` — capability declaration surface (POD).
- `app_version_info.h` — version/build metadata (POD).
- `app_failure_report.h` — structured failure payload (POD).

## Contract rules (derived)
- POD only; no behavior or defaults.
- Explicit version field in every struct.
- Deterministic ordering; TLV/JSON friendly.
- No dependencies on engine/game headers beyond shared core types.

## Source of truth
- The header files are authoritative for field definitions.
- This document must be updated when headers change.
