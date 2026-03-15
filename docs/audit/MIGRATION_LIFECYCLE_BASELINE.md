Status: DERIVED
Last Reviewed: 2026-03-14
Stability: provisional
Future Series: COMPAT/MIGRATION
Replacement Target: release-pinned migration bundles and stricter lifecycle enforcement after v0.0.0-mock

# Migration Lifecycle Baseline

## Policy Table

- `artifact.blueprint`
- `artifact.component_graph`
- `artifact.install_manifest`
- `artifact.install_plan`
- `artifact.instance_manifest`
- `artifact.negotiation_record`
- `artifact.pack_lock`
- `artifact.profile_bundle`
- `artifact.release_index`
- `artifact.release_manifest`
- `artifact.save`
- `artifact.session_template`

## Decision Examples

- legacy blueprint: `decision.migrate`
- future save: `decision.read_only`
- unknown policy: `decision.refuse` / `refusal.migration.no_path`

## Readiness

- migrate vs read-only vs refuse decisions are centralized in `src/compat/migration_lifecycle.py`
- save/install/instance validators emit `migration_decision_record`
- setup migration commands and standalone tools can route through the same deterministic planner/apply helpers

