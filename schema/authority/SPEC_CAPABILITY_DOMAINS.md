# SPEC CAPABILITY DOMAINS (OMNI0)

Status: draft.
Version: 1.0
Scope: capability scoping and domain constraints.

## Capability Scope
Capabilities are scoped by:
- domain (domain_id or domain volume set)
- time window (start/end ACT)
- subject type (actor, tool, system)
- parameter limits (quantitative caps)

## Scope Rules
- Scope is additive and explicit.
- Scope evaluation is deterministic.
- Denials override grants unless explicitly superseded.

## Integration Points
- DOMAIN volumes for spatial scope
- TIME windows for temporal scope
- LAW targets for governance
