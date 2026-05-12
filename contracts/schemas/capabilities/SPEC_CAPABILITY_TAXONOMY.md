# SPEC_CAPABILITY_TAXONOMY (OMNI0)

Schema ID: CAPABILITY_TAXONOMY
Schema Version: 1.0.0
Status: binding.
Scope: canonical capability identifiers and layer mapping.

## Purpose
Define a shared vocabulary for capabilities so all authority is expressed via
data-defined grants and denials, not modes or admin flags.

## Capability ID Format
- Uppercase ASCII with underscores.
- Grants use `CAN_` prefix.
- Denials use `DENY_` prefix (see `SPEC_NEGATIVE_CAPABILITIES.md`).
- Aliases are allowed but must reference canonical IDs.

## Canonical Capability Registry (Initial)
Capabilities are grouped by authority layer. This list may expand.

SIMULATION
- CAN_PLAY (composite baseline for standard play)
- CAN_SIMULATION_MUTATE
- CAN_BUILD
- CAN_SPAWN_SUBJECT
- CAN_DESTROY_SUBJECT
- CAN_TERRAIN_EDIT

SPATIAL
- CAN_TRAVEL
- CAN_TRAVEL_FORCE
- CAN_SPATIAL_ENTRY
- CAN_FREECAM

TEMPORAL
- CAN_TIME_VIEW
- CAN_TIME_SLOW_VIEW
- CAN_TIME_FAST_FORWARD
- CAN_FREEZE_SUBJECT

EPISTEMIC
- CAN_OBSERVE
- CAN_OBSERVE_HIDDEN
- CAN_INSPECT_HIDDEN_STATE
- CAN_INSPECT_ARCHIVAL

GOVERNANCE
- CAN_MODIFY_LAWS
- CAN_GRANT_CAPABILITIES
- CAN_OVERRIDE_CAPABILITIES

EXECUTION
- CAN_SELECT_BACKEND
- CAN_SET_BUDGET_PROFILE

INTEGRITY
- CAN_APPROVE_MODIFIED_CLIENTS
- CAN_USE_EXTERNAL_TOOLS

ARCHIVAL
- CAN_ARCHIVE_FREEZE
- CAN_FORK_TIMELINE
- CAN_HISTORY_PATCH

## Composite Capability Sets
Composite capabilities are data-defined sets of canonical capabilities.
Examples:
- CAN_PLAY may include baseline SIMULATION, SPATIAL, and EPISTEMIC grants.
- "Creative" or "Anarchy" profiles are declared as capability sets, not modes.

## Capability to Law Target Mapping
Each capability definition MUST declare:
- covered authority layers,
- required law targets,
- allowed effects (if any).

Example:
CAN_TRAVEL_FORCE -> law targets include AUTH.SPATIAL_OVERRIDE,
effect OP_TRAVEL_FORCE.

## Cross-References
- Negative capabilities: `schema/capabilities/SPEC_NEGATIVE_CAPABILITIES.md`
- Authority layers: `schema/authority/SPEC_AUTHORITY_LAYERS.md`
- Law targets: `schema/law/SPEC_LAW_TARGETS.md`
