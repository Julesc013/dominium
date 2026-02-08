Status: DERIVED
Last Reviewed: 2026-02-08
Supersedes: none
Superseded By: none

# Pack Capabilities

## Capability Naming
- Capability and entitlement identifiers MUST use reverse-DNS namespaced ids.
- Unknown capability ids are refusal conditions, not fallback paths.

## Required Fields
- `requires_capabilities` is mandatory and explicit.
- `provides_capabilities` is mandatory and explicit.
- `entitlements` is mandatory and explicit, including empty lists when none apply.
- `optional_capabilities` is optional and explicit when present.

## Validation Rules
- Pack validation rejects legacy stage/progression fields.
- Capability aliases (`depends`, `dependencies`, `provides`) must remain consistent with capability lists.
- Missing providers for required capabilities are refusal conditions.

## Refusal Behavior
- Missing required capabilities: capability refusal.
- Invalid capability ids: manifest invalid refusal.
- Legacy stage/progression fields: explicit migration refusal.
