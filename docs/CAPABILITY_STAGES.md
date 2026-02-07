Status: DERIVED
Last Reviewed: 2026-02-07
Supersedes: none
Superseded By: none

# CAPABILITY_STAGES

Stage identifiers are fixed data values used for capability gating:
- `STAGE_0_NONBIO_WORLD`
- `STAGE_1_NONINTELLIGENT_LIFE`
- `STAGE_2_INTELLIGENT_PRE_TOOL`
- `STAGE_3_PRE_TOOL_WORLD`
- `STAGE_4_PRE_INDUSTRY`
- `STAGE_5_PRE_PRESENT`
- `STAGE_6_FUTURE`

## Metadata rules

- `requires_stage` is mandatory on stage declarations and pack manifests.
- `provides_stage` is mandatory and MUST be greater than or equal to `requires_stage`.
- `stage_features` is mandatory and MUST be a list.
- `stage_features` keys MUST be namespaced/versioned tags (`<namespace+version>.<domain>.<feature>`).
- Absence of stage metadata is a refusal condition; there is no implicit fallback stage.

## Command gating rules

- Every canonical command descriptor MUST declare:
  - `required_stage`
  - `required_capabilities` (explicit list, may be empty)
  - `epistemic_scope`
- Command availability uses ordered stage comparison only.
- If world stage rank is lower than `required_stage`, command access is denied.
- UI bindings are valid only when action keys resolve to canonical command descriptors.

## UI IR gating rules

- UI enablement predicates are limited to:
  - `world_stage>=required_stage`
  - `world_stage>=<fixed_stage_id>`
  - `capability:<capability_id>`
  - `epistemic_permission` / `epistemic_permission:<token>`
  - `instance.selected`
  - `profile.present`
- Predicates outside this set fail `UI_BIND_PHASE`.
- UI bindings must not create command behavior outside the canonical registry.

## Failure modes and required reason codes

- `REFUSE_INVALID_STAGE`
  - Trigger: invalid or unknown stage id in stage metadata or request context.
- `REFUSE_CAPABILITY_STAGE_TOO_LOW`
  - Trigger: requested pack/command requires a higher stage than provided by world context.
- `REFUSE_CAPABILITY_MISSING`
  - Trigger: required capability is absent.
- `REFUSE_INTEGRITY_VIOLATION`
  - Trigger: missing mandatory stage fields or malformed `stage_features`.
