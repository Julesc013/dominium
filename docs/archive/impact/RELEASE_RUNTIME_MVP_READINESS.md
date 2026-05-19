Status: DERIVED
Last Reviewed: 2026-03-15
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: release-pinned impact note regenerated from governed release/runtime backlog

# Release Runtime MVP Readiness

This note maps the current release/runtime stabilization backlog to explicit player demand IDs so runtime-domain changes remain explainable under RepoX demand governance.

## Demand IDs

- `fact.plc_control_panel`
- `fact.deadlock_free_signaling`
- `city.smart_power_grid`
- `sci.open_data_trust_network`
- `sci.autonomous_lab_scheduler`

## Rationale

- Release/install/update/trust work affects whether controlled factory and infrastructure sessions can be installed, started, verified, replayed, and rolled back without silent drift.
- Capability negotiation, migration, observability, and archive retention affect whether those sessions remain inspectable, trustable, and reproducible for operators and researchers.
- MVP playtest hardening therefore directly supports the above demand surfaces even though the current changes are mostly ecosystem/runtime scaffolding rather than new simulation verbs.
