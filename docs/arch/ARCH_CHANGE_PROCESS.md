# Architectural Change Process (FUTURE0)

Status: binding.
Scope: the only valid process for architectural changes.

Deep changes require explicit, auditable process. No quick fixes.

## Invariants
- Invariants cannot be changed without explicit review and canon updates.
- Refusal is valid if invariants cannot be preserved.

## Required process
1) Propose change in a design doc (problem, scope, alternatives).
2) Identify invariant impact and compatibility risks.
3) Add a migration or refusal plan for data and schema.
4) Add CI guards and enforcement IDs.
5) Land on a feature branch with explicit review checkpoints.
6) Ratify into canon by updating ARCH0/CANON docs and the system map.

## Notes
- Changes that alter invariants must follow `docs/arch/CHANGE_PROTOCOL.md`.
- Architectural review is mandatory before merge.
- Refusal is valid if invariants cannot be preserved.

## Forbidden assumptions
- No direct-to-main changes for architectural shifts.
- No silent migration or schema changes without a plan.
- No bypass of review or CI enforcement.

## Dependencies
- Change protocol: `docs/arch/CHANGE_PROTOCOL.md`
- Canon and invariants: `docs/arch/INVARIANTS.md`

## See also
- `docs/arch/CHANGE_PROTOCOL.md`
- `docs/arch/INVARIANTS.md`
