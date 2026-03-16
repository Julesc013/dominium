Status: DERIVED
Last Reviewed: 2026-03-03
Supersedes: none
Superseded By: none
Version: 1.0.0
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# MOB-9 Maintenance And Wear Baseline

## Scope

This baseline formalizes deterministic mobility wear and maintenance across:
- infrastructure: track edges, corridors, signal/switch equipment
- vehicles: wheel, brake, engine wear

The implementation remains process-mediated and integrates with existing MAT/MECH/FIELD/MOB subsystems.

## Wear Types And Policies

Registries:
- `data/registries/wear_type_registry.json`
- `data/registries/wear_accumulation_policy_registry.json`
- `data/registries/maintenance_policy_registry.json` (mobility additions)

Canonical wear types:
- `wear.track`
- `wear.wheel`
- `wear.brake`
- `wear.engine`
- `wear.signal`
- `wear.switch`

Accumulation policy IDs:
- `accum.per_load_cycle`
- `accum.per_tick`
- `accum.environment_scaled`

Maintenance policy IDs:
- `maint.track_standard`
- `maint.vehicle_standard`
- `maint.signal_standard`

## Runtime Integration

Primary deterministic process handlers:
- `process.mobility_wear_tick`
- `process.mob_failure`
- `process.mob_track_failure`
- `process.inspect_track`
- `process.service_track`
- `process.inspect_vehicle`
- `process.service_vehicle`

Wear accumulation sources:
- `process.travel_tick` (macro/meso traversal and congestion effects)
- `process.mobility_micro_tick` (micro constrained motion and braking)
- `process.signal_tick` (signal/switch operational wear)

## Hazard And Incident Coupling

- Wear threshold crossings generate explicit incident/failure outputs.
- Track wear sets track failure markers and contributes to derail-risk pathways.
- Vehicle wear triggers failure incidents and speed-cap effects.
- Signal/switch wear activates signal hazard rows for interlocking/safety processing.

## Inspection And Service Lifecycle

- Inspection processes emit deterministic `mobility_inspection_snapshots`.
- Service processes reduce wear using deterministic reset fractions.
- Service supports deterministic material consumption via MAT logistics inventory when supplied.
- `process.mobility_wear_tick` advances maintenance schedules with `ScheduleComponent` semantics and produces due-event rows.

## Performance And Determinism Guarantees

- Wear rows are keyed deterministically by `(target_id, wear_type_id)`.
- Update application order is stable and sorted.
- Budget degrade path defers only deterministic suffix updates.
- Deferred updates are persisted in `mobility_wear_pending_updates`.
- Runtime state tracks processed/deferred counts and threshold crossings per tick.

## Extension Notes

The baseline is solver-light and compatible with future DOM integrations:
- corrosion/chemistry detail models can feed policy-scaled wear increments
- biological/weathering overlays can enrich environment scaling inputs
- deeper maintenance planning can attach to existing schedule and service process surfaces without truth-layer refactor

## Validation

Commands run:
- `python tools/xstack/repox/check.py --repo-root . --profile FAST`
- `python tools/xstack/auditx/check.py --repo-root . --profile STRICT`
- `python tools/xstack/testx/runner.py --repo-root . --profile STRICT --cache off --subset testx.mobility.wear.accumulation_deterministic,testx.mobility.wear.influences_derail_threshold,testx.mobility.wear.service_resets_wear,testx.mobility.wear.inspection_snapshot_stable,testx.mobility.wear.budget_degrade_wear_updates`
- `python tools/xstack/run.py strict --repo-root . --cache on`

Results:
- RepoX: `pass` (warning-only baseline findings outside MOB-9 scope)
- AuditX: `pass` (scan complete; warning-only baseline findings outside MOB-9 scope)
- TestX MOB-9 subset: `pass` (5/5)
- strict build: `refusal` due pre-existing repository baseline failures (CompatX lockfile/session/testx/package steps), not introduced by MOB-9 changes
