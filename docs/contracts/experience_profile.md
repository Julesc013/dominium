Status: DERIVED
Last Reviewed: 2026-02-14
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `schemas/experience_profile.schema.json` v1.0.0 and CompatX `tools/xstack/compatx/version_registry.json`.

# ExperienceProfile Contract

## Purpose
Define the canonical experience binding for presentation defaults, lens allowances, transition policy, and default law binding.

## Source of Truth
- Schema: `schemas/experience_profile.schema.json` (`version: 1.0.0`)
- Registry projection: `build/registries/experience.registry.json`
- Canon binding: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`

## Required Fields (`v1.0.0`)
- `schema_version` (`const "1.0.0"`)
- `experience_id` (string)
- `presentation_defaults` (`default_lens_id`, `hud_layout_id`)
- `allowed_lenses` (array of lens ids)
- `suggested_parameter_bundles` (array of parameter bundle ids)
- `allowed_transitions` (array of experience ids)
- `default_law_profile_id` (string)

## Invariants
- ExperienceProfile encodes presentation/policy binding only; it does not encode mechanics.
- Lens access remains law-gated and authority-gated even when listed in `allowed_lenses`.
- Unknown top-level fields are refused in strict schema validation.
- Session boot and script execution resolve default lens through compiled `experience.registry`.

## Example JSON (`profile.lab.developer`)
```json
{
  "schema_version": "1.0.0",
  "experience_id": "profile.lab.developer",
  "presentation_defaults": {
    "default_lens_id": "lens.diegetic.sensor",
    "hud_layout_id": "hud.lab.navigation"
  },
  "allowed_lenses": [
    "lens.diegetic.sensor",
    "lens.nondiegetic.debug"
  ],
  "suggested_parameter_bundles": [
    "params.lab.placeholder",
    "params.lab.precision_nav"
  ],
  "allowed_transitions": [
    "experience.lab.galaxy"
  ],
  "default_law_profile_id": "law.lab.unrestricted"
}
```

## TODO
- Add transition refusal semantics for cross-experience handoff.
- Add canonical mission-binding guidance once mission contracts are formalized.
- Add migration examples for future ExperienceProfile major updates.

## Cross-References
- `docs/contracts/law_profile.md`
- `docs/contracts/session_spec.md`
- `docs/architecture/session_lifecycle.md`
- `docs/architecture/pack_system.md`
