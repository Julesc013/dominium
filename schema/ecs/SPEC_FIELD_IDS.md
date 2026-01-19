# SPEC_FIELD_IDS (ECSX0)

Schema ID: ECS_FIELD_IDS  
Schema Version: 1.0.0  
Status: binding.  
Scope: stable field_id assignment and lifecycle rules.

## Purpose
Provide a deterministic, auditable field_id policy that prevents reuse,
preserves meaning across versions, and enables skip-unknown behavior.

## Field ID Requirements
- `field_id` is a stable identifier for field meaning.
- `field_id` MUST never be reused for a different meaning.
- Removing a field is a **deprecation**, not a reuse.
- Renaming is allowed if `field_id` does not change.

## Assignment Policy
Allowed schemes:
1) **Numeric allocation**:
   - Small integer IDs assigned in a stable registry.
   - Reserve ranges for engine vs game ownership.
2) **Stable hash**:
   - Deterministic hash of a canonical token (e.g., `COMPONENT.FIELD`).
   - Hash method must be fixed and documented.

Constraints:
- Hash collisions are forbidden; collision requires new token or numeric override.
- IDs MUST be unique within a component.

## Suggested Ranges
These ranges are advisory and must be enforced by registry tooling:
- `1..999`: engine-owned fields
- `1000..9999`: game-owned fields
- `10000+`: mod extensions (game-owned only)

## Deprecation Rules
Deprecated fields:
- must remain in schema with status `deprecated`,
- must be preserved in serialization (skip-unknown safe),
- must not be reintroduced with different semantics.

## Forbidden
- Reusing IDs.
- Assigning IDs based on runtime addresses or container order.
- Implicit field IDs derived from declaration order.
