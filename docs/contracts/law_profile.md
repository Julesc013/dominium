Status: DERIVED
Last Reviewed: 2026-02-14
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `schemas/law_profile.schema.json` v1.0.0 and CompatX `tools/xstack/compatx/version_registry.json`.

# LawProfile Contract

## Purpose
Define the canonical law profile payload used to allow/refuse process classes and lens access.

## Source of Truth
- Schema: `schemas/law_profile.schema.json` (`version: 1.0.0`)
- Related: `docs/contracts/lens_contract.md`
- Canon binding: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`

## Required Fields (`v1.0.0`)
- `schema_version` (`const "1.0.0"`)
- `law_profile_id` (string)
- `allowed_processes` (array of strings)
- `forbidden_processes` (array of strings)
- `allowed_lenses` (array of strings)
- `epistemic_limits` (object)
- `respawn_rules` (object)
- `debug_allowances` (object)

## Invariants
- Law is profile data, never a runtime mode branch.
- Allowed/forbidden process sets are explicit; no implicit fallback grants.
- Lens access remains law-gated and authority-scoped.
- Unknown top-level fields are refused by strict schema validation.
- Observation execution must refuse on lens policy violations with `LENS_FORBIDDEN`.
- Law payload used by Observation Kernel must include `allowed_lenses` and `epistemic_limits`.
- Process execution must refuse with deterministic reason codes:
  - `PROCESS_FORBIDDEN`
  - `ENTITLEMENT_MISSING`
  - `PRIVILEGE_INSUFFICIENT`

## Lab Process IDs (`law.lab.unrestricted`)
- `process.camera_move`
- `process.camera_teleport`
- `process.region_management_tick`
- `process.time_control_set_rate`
- `process.time_pause`
- `process.time_resume`

## Lab Entitlement Mapping (`law.lab.unrestricted`)
- `process.camera_move` -> `entitlement.camera_control`
- `process.camera_teleport` -> `entitlement.teleport`
- `process.region_management_tick` -> `session.boot`
- `process.time_control_set_rate` -> `entitlement.time_control`
- `process.time_pause` -> `entitlement.time_control`
- `process.time_resume` -> `entitlement.time_control`

## Example JSON (`schemas/law_profile.schema.json`)
```json
{
  "schema_version": "1.0.0",
  "law_profile_id": "law.lab.unrestricted",
  "allowed_processes": [
    "process.camera_move",
    "process.camera_teleport",
    "process.region_management_tick",
    "process.time_control_set_rate",
    "process.time_pause",
    "process.time_resume"
  ],
  "forbidden_processes": [],
  "allowed_lenses": [
    "lens.diegetic.sensor",
    "lens.nondiegetic.debug"
  ],
  "epistemic_limits": {
    "max_view_radius_km": 1000000000,
    "allow_hidden_state_access": true
  },
  "respawn_rules": {
    "respawn_allowed": false,
    "respawn_delay_seconds": 0
  },
  "debug_allowances": {
    "allow_nondiegetic_overlays": true,
    "allow_time_dilation_controls": true
  },
  "process_entitlement_requirements": {
    "process.camera_move": "entitlement.camera_control",
    "process.camera_teleport": "entitlement.teleport",
    "process.region_management_tick": "session.boot",
    "process.time_control_set_rate": "entitlement.time_control",
    "process.time_pause": "entitlement.time_control",
    "process.time_resume": "entitlement.time_control"
  },
  "process_privilege_requirements": {
    "process.camera_move": "observer",
    "process.camera_teleport": "operator",
    "process.region_management_tick": "observer",
    "process.time_control_set_rate": "operator",
    "process.time_pause": "operator",
    "process.time_resume": "operator"
  }
}
```

## TODO
- Add compatibility guidance for conflicting process lists.
- Add canonical debug allowance taxonomy once debug registry exists.
- Add migration notes for future law-profile major bumps.
- Add explicit policy for nondiegetic lens authorization by privilege level.

## Cross-References
- `docs/contracts/lens_contract.md`
- `docs/contracts/refusal_contract.md`
- `docs/contracts/versioning_and_migration.md`
- `docs/architecture/pack_system.md`
- `docs/architecture/lens_system.md`
- `docs/architecture/camera_and_navigation.md`
