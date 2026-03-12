Status: DERIVED
Last Reviewed: 2026-02-08
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Pack Capabilities

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


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
