Status: DRAFT
Version: 1.0.0-draft
Last Reviewed: 2026-02-14
Compatibility: Derived from `schema/session/session_spec.schema` v1.1.0 and bound to canon v1.0.0.

# SessionSpec Contract

## Purpose
Define the canonical launch/session composition payload used by launcher/client/server orchestration.

## Source of Truth
- Schema: `schema/session/session_spec.schema`
- Related: `schema/authority/authority_context.schema`
- Canon binding: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`

## Intended Contract Fields (Required)
- `session_id: id`
- `universe_id: id`
- `save_id: id`
- `scenario_id: id`
- `mission_id: id`
- `experience_id: id`
- `parameter_bundle_id: id`
- `pack_lock_hash: tag`
- `authority_context: id`
- `budget_policy_id: id`
- `fidelity_policy_id: id`
- `replay_policy: enum(recording_enabled|recording_disabled)`
- `deterministic_seed_bundle: [id]`
- `workspace_id: tag`
- `extensions: map`

## Invariants
- SessionSpec describes references and authority context; it does not change simulation semantics.
- Session composition must remain profile-driven; no mode flags.
- `pack_lock_hash` must identify deterministic pack resolution inputs.
- `authority_context` must resolve to a valid authority context object before intent admission.
- `extensions` is open-map and must preserve unknown keys.

## Example
```yaml
session_spec:
  session_id: session.lab_galaxy.nav_001
  universe_id: universe.lab.main
  save_id: save.none
  scenario_id: scenario.lab.galaxy_nav
  mission_id: mission.lab.explore_corridor
  experience_id: experience.lab
  parameter_bundle_id: params.lab.default
  pack_lock_hash: lock.sha256.58f3...
  authority_context: authority.lab.observer
  budget_policy_id: budget.lab.default
  fidelity_policy_id: fidelity.lab.macro_first
  replay_policy: recording_enabled
  deterministic_seed_bundle:
    - seed.world.main
    - seed.nav.overlay
  workspace_id: ws.lab.navigation
  extensions: {}
```

## TODO
- Add JSON Schema excerpt once contract extractor tooling is introduced.
- Add lifecycle state chart for SessionSpec creation, negotiation, and activation.
- Add explicit refusal mapping for invalid/missing field classes.

## Cross-References
- `docs/contracts/authority_context.md`
- `docs/architecture/time_model.md`
- `docs/architecture/pack_system.md`

