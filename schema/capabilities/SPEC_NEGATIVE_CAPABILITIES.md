# SPEC_NEGATIVE_CAPABILITIES (OMNI0)

Schema ID: NEGATIVE_CAPABILITIES
Schema Version: 1.0.0
Status: binding.
Scope: explicit denial capabilities and precedence rules.

## Purpose
Define explicit denials so restrictions are expressed as data, not implied
absence or hidden code paths.

## Denial Rules
- Denials are explicit `DENY_*` capabilities.
- Absence of a capability is not a denial.
- Denials take precedence over grants unless explicitly overridden.
- Overrides must be explicit, auditable effects.

## Canonical Denials (Initial)
SIMULATION
- DENY_SIMULATION_MUTATION
- DENY_SPAWN_SUBJECT
- DENY_DESTROY_SUBJECT
- DENY_TERRAIN_EDIT

SPATIAL
- DENY_SPATIAL_ENTRY
- DENY_TRAVEL_FORCE
- DENY_FREECAM

TEMPORAL
- DENY_TIME_DILATION
- DENY_TIME_FAST_FORWARD
- DENY_FREEZE_SUBJECT

EPISTEMIC
- DENY_EPISTEMIC_ACCESS
- DENY_OBSERVE_HIDDEN
- DENY_INSPECT_ARCHIVAL

GOVERNANCE
- DENY_LAW_MODIFICATION
- DENY_CAPABILITY_GRANT
- DENY_CAPABILITY_OVERRIDE

INTEGRITY
- DENY_MODIFIED_CLIENTS
- DENY_EXTERNAL_TOOLS

ARCHIVAL
- DENY_FORK_TIMELINE
- DENY_HISTORY_PATCH
- DENY_ARCHIVAL_OVERRIDE

## Override Semantics
Overrides are lawful only when:
- a higher-scope capability explicitly permits the override,
- an explicit effect token is emitted,
- the audit log includes the denial that was overridden.

## Cross-References
- Capability taxonomy: `schema/capabilities/SPEC_CAPABILITY_TAXONOMY.md`
- Law effects: `schema/law/SPEC_LAW_EFFECTS.md`
