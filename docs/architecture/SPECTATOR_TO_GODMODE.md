# Spectator to Godmode (OMNI0)

Status: binding.
Scope: authority spectrum as data-defined capability profiles.

## Purpose
Define a single, composable authority system where spectator, competitive,
anarchy, and omnipotent control are expressed through the same primitives.

Profiles are data only; they are not modes and do not imply code paths.

## Invariants
- Profiles are data-defined; no hard-coded modes exist.
- Capabilities are additive; denials are explicit.
- Law and audit gates remain mandatory.

## Canonical Profiles (Examples)
SPECTATOR_ONLY
- Capabilities: CAN_OBSERVE
- Denials: DENY_SIMULATION_MUTATION, DENY_SPAWN_SUBJECT, DENY_DESTROY_SUBJECT,
  DENY_TERRAIN_EDIT, DENY_TRAVEL_FORCE

COMPETITIVE_LOCKDOWN
- Capabilities: CAN_PLAY
- Denials: DENY_MODIFIED_CLIENTS, DENY_EXTERNAL_TOOLS, DENY_TIME_DILATION

STANDARD_SURVIVAL
- Capabilities: CAN_PLAY, CAN_BUILD, CAN_TRAVEL
- Denials: none (law enforces normal constraints)

CREATIVE
- Capabilities: CAN_SIMULATION_MUTATE, CAN_BUILD, CAN_TRAVEL, CAN_FREECAM
- Denials: DENY_LAW_MODIFICATION, DENY_HISTORY_PATCH

ANARCHY
- Capabilities: almost all layers
- Denials: none except existence invariants

META_ANARCHY
- Capabilities: CAN_MODIFY_LAWS, CAN_GRANT_CAPABILITIES
- Denials: DENY_HISTORY_PATCH (fork required)

OMNIPOTENT_ADMIN
- Capabilities: all layers
- Denials: none, except archived history requires fork and audit

Profiles are examples, not limits.

## Scope Integration
Capability grants and denials are scoped by:
- domain volumes and travel paths,
- ACT time windows,
- subject types and jurisdictions.

Examples:
- Freecam allowed only inside a dedicated admin chamber volume.
- Spectator-only zones that deny mutation.

## Forbidden assumptions
- Profiles can bypass law gates.
- "Godmode" implies unaudited mutation.

## Dependencies
- Authority layers: `schema/authority/SPEC_AUTHORITY_LAYERS.md`
- Capability domains: `schema/authority/SPEC_CAPABILITY_DOMAINS.md`

## See also
- `schema/authority/SPEC_CAPABILITY_DOMAINS.md`
- `schema/capabilities/SPEC_CAPABILITY_TAXONOMY.md`
- `docs/arch/AUTHORITY_IN_REALITY.md`
