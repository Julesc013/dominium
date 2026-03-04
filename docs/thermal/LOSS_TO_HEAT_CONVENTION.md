# Loss-To-Heat Convention

Status: CANONICAL  
Last Updated: 2026-03-03  
Scope: Cross-domain dissipated-energy mapping contract (THERM-0 Phase 4).

## 1) Rule

Any dissipated energy in any domain must be represented as one of:

1. Preferred: `quantity.heat_loss` output (or compatible `quantity.thermal.heat_loss_stub` during migration).
2. Fallback: `effect.temperature_increase_local` when quantity pipeline is unavailable.

Direct silent loss sinks are forbidden.

## 2) Attribution

Every loss-to-heat emission must carry deterministic attribution in artifact/event metadata:

- source domain id
- source process id
- target id (node/edge/device/volume/channel)
- tick

## 3) Replayability

Loss-to-heat outputs are replay-significant and must be logged through process/event pathways.

- No hidden implicit dissipation.
- No renderer/UI-side thermal mutation.

## 4) Migration Guidance

Legacy systems emitting heat-like values should migrate to:

- canonical `quantity.heat_loss` outputs through model/flow paths
- or temporary `quantity.thermal.heat_loss_stub` with declared migration notes

## 5) Governance

RepoX invariant (warn-phase in THERM-0):

- `INV-LOSS-MAPPED-TO-HEAT`

AuditX smell:

- `HeatLossBypassSmell`

