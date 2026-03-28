Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: release-pinned impact note regenerated from governed release/runtime backlog

# Omega Prep Runtime Hardening

Change:
- Pre-Ω runtime hardening for CI lane migration, validation boundary hygiene, and client build portability fixes.

Touched Paths:
- `.github/workflows/ci.yml`
- `.github/workflows/xstack_lanes.yml`
- `client/app/main_client.c`
- `client/core/session_artifacts.h`
- `validation/validation_engine.py`
- `tools/xstack/repox/check.py`

Demand IDs:
- `fact.plc_control_panel`
- `fact.deadlock_free_signaling`
- `city.smart_power_grid`
- `sci.open_data_trust_network`
- `sci.autonomous_lab_scheduler`

Notes:
- These changes harden the deterministic runtime and release-verification path without adding new gameplay semantics.
- CI lane migration keeps packaging, verification, and demand-governed runtime checks aligned ahead of Ω gating.
