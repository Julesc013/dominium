# Mobility Extension Contract

Status: CANONICAL
Last Updated: 2026-03-03
Scope: MOB-11 extension rules for adding new vehicle classes and movement domains.

## 1) Purpose

This contract defines how mobility extensions must integrate without violating deterministic, process-only, and control-plane invariants.

## 2) Invariants

All extensions must preserve:

- process-only mutation (`A2`)
- deterministic outcomes across thread/platform variants (`A1`)
- no runtime mode flags (`A4`)
- explicit degradation/refusal under budget pressure (`A10`)
- pack/registry-driven optionality (`A9`)

## 3) New Vehicle Class Requirements

Every new vehicle class must:

- register a unique `vehicle_class_id` in `data/registries/vehicle_class_registry.json`
- declare `supported_motion_modes` only via registry/spec data
- define required interfaces through `spec_ids`/required specs
- map control authority through `PoseSlots` + `ControlBinding`
- integrate ports/interior/mount references through assembly metadata

Forbidden:

- hardcoded per-class runtime branches
- direct motion mutation from UI/renderer/input paths

## 4) GuideGeometry Requirements

All guided movement must bind to MOB-1 GuideGeometry:

- use `geometry_type_registry` ids (`geo.*`)
- use deterministic snapping/metrics pipeline
- store formal artifacts only through geometry processes
- keep inferred candidates derived-only until acceptance

Extensions must not bypass GuideGeometry by introducing ad-hoc path primitives.

## 5) MobilityNetwork and Occupancy Requirements

Networked movement extensions must:

- map traversable connectivity into MobilityNetworkGraph payloads
- use node/edge kinds from mobility registries (or add new kinds via registry update)
- integrate occupancy and congestion through MOB-5 traffic engine
- preserve deterministic routing tie-break rules

Any capacity/reservation semantics must be encoded in policy/registry data, never hardcoded.

## 6) Control Plane Requirements

All movement initiation and mutation must flow through CTRL:

- planner/scheduler/manual actions resolve to control intents/processes
- fidelity transitions use negotiation/arbitration, not local one-off logic
- downgrades/refusals/incidents emit decision-log markers and event artifacts

Client input cannot directly author authoritative movement state.

## 7) New Movement Domain Requirements

For new domains (for example orbital, maglev, field-following):

- add/extend `geometry_type` registry + schema refs
- add deterministic spec-compliance checks (and refusal codes where needed)
- provide deterministic route/constraint compatibility hooks
- integrate with field/effect surfaces through FieldLayer queries only
- integrate with RS fidelity arbitration for ROI activation and collapse

No domain may introduce always-on global micro simulation.

## 8) Compatibility and Migration

When extension contracts require schema/registry changes:

- follow semver + CompatX policy
- provide explicit migration or explicit refusal path
- preserve open-map `extensions` behavior where required

Optional extension packs must degrade/refuse deterministically when absent.

## 9) Verification Requirements

Extension PRs must include:

- deterministic tests for create/update/replay paths
- regression hash updates only with explicit required baseline tag
- AuditX/RepoX checks for bypass smells
- strict build + TestX pass evidence

## 10) Non-Goals

- This contract does not define domain-specific physics solvers.
- This contract does not permit control-plane bypass for prototyping.
- This contract does not permit runtime mode-flag forks.
