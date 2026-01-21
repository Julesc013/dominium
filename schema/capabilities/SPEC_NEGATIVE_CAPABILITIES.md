# SPEC NEGATIVE CAPABILITIES (OMNI0)

Status: draft.
Version: 1.0
Scope: explicit denial capabilities and precedence rules.

## Definition
Negative capabilities are explicit denials that override grants unless
explicitly superseded by higher authority.

## Canonical Denials (examples)
- DENY_SIMULATION_MUTATION
- DENY_SPATIAL_ENTRY
- DENY_TIME_DILATION
- DENY_EPISTEMIC_ACCESS
- DENY_LAW_MODIFICATION
- DENY_MODIFIED_CLIENTS
- DENY_EXTERNAL_TOOLS
- DENY_TIME_MANIPULATION

## Precedence
- Negative capabilities take precedence over grants.
- Overrides must be explicit and auditable.

## Integration Points
- Law targets for denial enforcement
- Domain/time scoping
