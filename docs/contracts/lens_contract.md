Status: DRAFT
Version: 1.0.0-draft
Last Reviewed: 2026-02-14
Compatibility: Derived from `schema/lens/lens.schema` v1.1.0 and `schema/governance/presentation_matrix.schema` v1.0.0.

# Lens Contract

## Purpose
Define law-governed observation/presentation channels without leaking authoritative truth or introducing mode branches.

## Source of Truth
- Schema: `schema/lens/lens.schema`
- Schema: `schema/governance/presentation_matrix.schema`
- Canon binding: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`

## Intended Contract Fields (Lens Registry)
`lens_registry` requires:
- `registry_id: id`
- `registry_version: semver`
- `schema_version_ref: tag`
- `lenses: [lens]`
- `extensions: map`

`lens` requires:
- `lens_id: id`
- `category: enum(diegetic|nondiegetic)`
- `required_entitlements: [id]`
- `requires_authority_level: id`
- `allowed_experiences: [id]`
- `watermark_policy: enum(none|observer|dev)`
- `description: text`
- `extensions: map`

## Intended Contract Fields (Presentation Matrix)
`presentation_matrix` requires:
- `registry_id: id`
- `registry_version: tag`
- `schema_version_ref: tag`
- `rows: [presentation_row]`
- `extensions: map`

`presentation_row` requires:
- `law_profile_id: id`
- `allowed_lenses: [id]`
- `allowed_ui_packs: [id]`
- `allowed_panels: [id]`
- `allowed_commands: [id]`
- `required_entitlements: [id]`
- `watermark_required: bool`
- `extensions: map`

## Invariants
- Lens contracts control perception/presentation only; they do not change gameplay or simulation outcomes.
- Lens visibility must be entitlement- and law-gated.
- Observer-Renderer-Truth separation must remain intact.
- Unknown fields in open maps (`extensions`) must be preserved.

## Example
```yaml
lens:
  lens_id: lens.diegetic.sensor
  category: diegetic
  required_entitlements: [client.ui.sensor]
  requires_authority_level: authority.observer
  allowed_experiences: [experience.lab, experience.survival]
  watermark_policy: observer
  description: "Sensor-limited diegetic cockpit feed."
  extensions: {}
```

```yaml
presentation_row:
  law_profile_id: law.lab.observe_only
  allowed_lenses: [lens.diegetic.sensor]
  allowed_ui_packs: [ui.lab.minimal]
  allowed_panels: [panel.map, panel.timeline]
  allowed_commands: [cmd.observe.focus]
  required_entitlements: [client.ui.map]
  watermark_required: true
  extensions: {}
```

## TODO
- Add deterministic precedence rules when multiple rows match equivalent contexts.
- Add refusal mapping for invalid lens entitlement combinations.
- Add migration examples for lens category expansion.

## Cross-References
- `docs/contracts/law_profile.md`
- `docs/architecture/truth_model.md`
- `docs/architecture/observation_kernel.md`

