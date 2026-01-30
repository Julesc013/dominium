# Decay, Erosion, Regeneration (TERRAIN0)

Status: binding.
Scope: event-driven terrain change; no per-tick global erosion.

## Locked rules
- No per-tick global erosion.
- All decay, erosion, and regeneration occurs via scheduled macro events.
- Events are deterministic and replayable.
- Effects are field/overlay updates, not mesh edits.

## Scheduling
Decay/erosion/regeneration events:
- are emitted by Processes.
- use deterministic ordering and explicit budgets.
- record provenance and refusal outcomes.

## Outputs
Events may emit:
- `delta_phi` overlays for erosion or fill.
- `delta_material` overlays for material changes.
- `delta_field` overlays for environment adjustments.

## See also
- `docs/architecture/PROCESS_ONLY_MUTATION.md`
- `docs/architecture/DETERMINISTIC_ORDERING_POLICY.md`
