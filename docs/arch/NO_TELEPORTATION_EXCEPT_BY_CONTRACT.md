# No Teleportation Except by Contract (TRAVEL0)

Status: draft.
Scope: explicit prohibition of implicit teleportation.

## Rule
No entity, asset, or actor may change location without an explicit travel
edge and scheduled travel effect.

## Allowed Exceptions
Only explicit travel edges may resolve to zero traversal time, and they still
must be scheduled and auditable. Examples:
- portals
- wormholes
- hyperlanes
- warp corridors

## Prohibitions
- No hidden "teleport" code paths.
- No direct position mutation without travel effects.
- No bypass of reachability and visitability gates.

## Audit and Enforcement
- Travel effects record origin, destination, edge, and schedule.
- Violations are refused, not patched around.

## References
- `docs/arch/TRAVEL_AND_MOVEMENT.md`
- `schema/travel/SPEC_TRAVEL_EDGES.md`
